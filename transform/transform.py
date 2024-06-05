import sys
import logging
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, sum as _sum, year, month, dayofmonth, date_format

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the arguments from the Glue job
args = getResolvedOptions(sys.argv, [
    'JOB_NAME', 'AWS_REGION', 'ATHENA_DATABASE', 'ATHENA_OUTPUT_BUCKET',
    'REDSHIFT_USER', 'REDSHIFT_PASSWORD', 'REDSHIFT_JDBC_URL', 'REDSHIFT_DATABASE', 'REDSHIFT_SCHEMA'
])

# Initialize the Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Function to read from Athena
def read_from_athena(database, table_name):
    try:
        athena_query = f"SELECT * FROM {database}.{table_name}"
        df = spark.read.format("jdbc") \
            .option("url", f"jdbc:awsathena://AwsRegion={args['AWS_REGION']};") \
            .option("dbtable", f"({athena_query}) as t") \
            .option("s3_staging_dir", f"s3://{args['ATHENA_OUTPUT_BUCKET']}/") \
            .option("driver", "com.simba.athena.jdbc.Driver") \
            .load()
        logger.info(f"Successfully read table {table_name} from Athena")
        return DynamicFrame.fromDF(df, glueContext, table_name)
    except Exception as e:
        logger.error(f"Error reading table {table_name} from Athena: {str(e)}")
        raise

# Function to write to Redshift
def write_to_redshift(dyf, table_name):
    try:
        glueContext.write_dynamic_frame.from_jdbc_conf(
            frame=dyf,
            catalog_connection="your_redshift_connection",
            connection_options={
                "dbtable": table_name,
                "database": args['REDSHIFT_DATABASE'],
                "user": args['REDSHIFT_USER'],
                "password": args['REDSHIFT_PASSWORD'],
                "redshiftTmpDir": f"s3://{args['ATHENA_OUTPUT_BUCKET']}/temp/"
            }
        )
        logger.info(f"Successfully wrote table {table_name} to Redshift")
    except Exception as e:
        logger.error(f"Error writing table {table_name} to Redshift: {str(e)}")
        raise

try:
    # Read data from Athena
    boletim_dyf = read_from_athena(args['ATHENA_DATABASE'], "boletim")
    caso_dyf = read_from_athena(args['ATHENA_DATABASE'], "caso")
    caso_full_dyf = read_from_athena(args['ATHENA_DATABASE'], "caso_full")
    obito_cartorio_dyf = read_from_athena(args['ATHENA_DATABASE'], "obito_cartorio")

    # Process boletim table to skip the header row
    boletim_df = boletim_dyf.toDF()
    boletim_df = boletim_df.filter(boletim_df.col0 != 'date')  # Remove header row

    # Correctly handle the header issue
    if boletim_df.head()[0] == 'date':
        boletim_df = boletim_df.filter(boletim_df.date != 'date')

    boletim_df = boletim_df.withColumnRenamed("col0", "date") \
                           .withColumnRenamed("col1", "notes") \
                           .withColumnRenamed("col2", "state") \
                           .withColumnRenamed("col3", "url")

    # Ensure date and state columns are in correct format
    boletim_df = boletim_df.withColumn("date", col("date").cast("date"))

    # Derive Date Dimension from both `boletim` and `caso`
    boletim_dates_df = boletim_df.select(col("date").cast("date").alias("date"))
    caso_df = caso_dyf.toDF()
    caso_dates_df = caso_df.select(col("date").cast("date").alias("date"))

    # Union the dates from both sources and remove duplicates
    all_dates_df = boletim_dates_df.union(caso_dates_df).distinct()

    # Create Date Dimension Table
    date_dim_df = all_dates_df.select(
        col("date").alias("date"),
        col("date").alias("date_key"),
        year("date").alias("year"),
        month("date").alias("month"),
        dayofmonth("date").alias("day"),
        date_format("date", "E").alias("weekday")
    ).distinct()
    date_dim_dyf = DynamicFrame.fromDF(date_dim_df, glueContext, "date_dim")
    write_to_redshift(date_dim_dyf, f"{args['REDSHIFT_SCHEMA']}.dim_date")

    # Create Location Dimension Table
    location_dim_df = caso_df.select(
        col("state"),
        col("city"),
        col("city_ibge_code").alias("location_key"),
        col("place_type")
    ).distinct()
    location_dim_dyf = DynamicFrame.fromDF(location_dim_df, glueContext, "location_dim")
    write_to_redshift(location_dim_dyf, f"{args['REDSHIFT_SCHEMA']}.dim_location")

    # Create Cause Dimension Table
    obito_cartorio_df = obito_cartorio_dyf.toDF()
    cause_dim_df = obito_cartorio_df.select(
        col("deaths_indeterminate_2019"),
        col("deaths_respiratory_failure_2019"),
        col("deaths_others_2019"),
        col("deaths_pneumonia_2019"),
        col("deaths_septicemia_2019"),
        col("deaths_sars_2019"),
        col("deaths_covid19")
    ).distinct().withColumnRenamed("deaths_covid19", "cause_name")
    cause_dim_df = cause_dim_df.withColumn("cause_key", col("cause_name"))
    cause_dim_dyf = DynamicFrame.fromDF(cause_dim_df, glueContext, "cause_dim")
    write_to_redshift(cause_dim_dyf, f"{args['REDSHIFT_SCHEMA']}.dim_cause")

    # Create Fact Table for Covid Cases
    fact_covid_cases_df = caso_df.groupBy("date", "state", "city", "place_type").agg(
        _sum("confirmed").alias("total_confirmed"),
        _sum("deaths").alias("total_deaths"),
        _sum("estimated_population_2019").alias("estimated_population_2019"),
        _sum("estimated_population").alias("estimated_population"),
        _sum("confirmed_per_100k_inhabitants").alias("confirmed_per_100k_inhabitants")
    ).withColumnRenamed("date", "date_key") \
     .withColumnRenamed("city_ibge_code", "location_key")
    fact_covid_cases_dyf = DynamicFrame.fromDF(fact_covid_cases_df, glueContext, "fact_covid_cases")
    write_to_redshift(fact_covid_cases_dyf, f"{args['REDSHIFT_SCHEMA']}.fact_covid_cases")

    # Create Fact Table for Covid Deaths
    fact_covid_deaths_df = obito_cartorio_df.select(
        col("date"),
        col("state"),
        col("deaths_covid19").alias("covid19_deaths"),
        col("deaths_total_2019"),
        col("deaths_total_2020")
    ).withColumnRenamed("date", "date_key") \
     .withColumnRenamed("state", "location_key") \
     .withColumnRenamed("deaths_covid19", "cause_key")
    fact_covid_deaths_dyf = DynamicFrame.fromDF(fact_covid_deaths_df, glueContext, "fact_covid_deaths")
    write_to_redshift(fact_covid_deaths_dyf, f"{args['REDSHIFT_SCHEMA']}.fact_covid_deaths")

    logger.info("Job completed successfully")

except Exception as e:
    logger.error(f"Job failed: {str(e)}")
    raise

finally:
    # Commit the job
    job.commit()
