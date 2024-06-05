import boto3
import redshift_connector
from pyathena import connect
from pyathena.util import as_pandas

# AWS credentials and configurations
athena_database = 'your_athena_database'
redshift_database = 'your_redshift_database'
redshift_user = 'your_redshift_user'
redshift_password = 'your_redshift_password'
redshift_host = 'your_redshift_host'
redshift_port = 'your_redshift_port'

# Define the queries to extract data from Athena
queries = {
    "boletim": "SELECT * FROM boletim",
    "caso": "SELECT * FROM caso",
    "caso_full": "SELECT * FROM caso_full",
    "obito_cartorio": "SELECT * FROM obito_cartorio"
}

# Athena connection
athena_conn = connect(s3_staging_dir='s3://your-athena-staging-bucket/',
                      region_name='your-region')

# Redshift connection
redshift_conn = redshift_connector.connect(
    host=redshift_host,
    database=redshift_database,
    user=redshift_user,
    password=redshift_password,
    port=redshift_port
)

def load_to_redshift(df, table_name):
    cursor = redshift_conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    for index, row in df.iterrows():
        columns = ', '.join(row.index)
        values = ', '.join([f"'{str(value)}'" for value in row.values])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        cursor.execute(insert_sql)
    cursor.close()

# Extract, transform, and load data
for table_name, query in queries.items():
    # Extract data from Athena
    df = as_pandas(athena_conn.execute(query))
    
    # Transform data (example transformation, adjust as needed)
    if table_name == "caso":
        df['date'] = pd.to_datetime(df['date'])
    
    # Load data into Redshift
    load_to_redshift(df, table_name)

# Close connections
athena_conn.close()
redshift_conn.close()