from manager import AWSManager
from dotenv import load_dotenv
import os
from loguru import logger
import sys

# Load environment variables from .env file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
s3_bucket = os.getenv('S3_BUCKET_PARQUET')

# List of tables in the covid19_dataset database
tables = [
    "boletim", "caso", "caso_full", "obito_cartorio"
]

class DataManager:
    """
    Manages data operations including fetching data from Athena,
    converting them to Parquet, and uploading them to S3.
    """

    def __init__(self, aws_manager: AWSManager):
        """
        Initializes DataManager with AWS manager.
        Args:
            aws_manager (AWSManager): Instance of AWSManager to handle AWS operations.
        """
        self.aws_manager = aws_manager

    def query_and_save_to_s3(self, table_name: str):
        """
        Queries data from Athena, converts it to Parquet, and uploads to S3.
        Args:
            table_name (str): The name of the table to query.
        """
        try:
            sql_query = f"SELECT * FROM covid19_dataset.{table_name}"
            s3_output = f"s3://{s3_bucket}/{table_name}/"

            logger.info(f"Querying data from table {table_name}")
            self.aws_manager.query_athena_to_s3(sql_query, "covid19_dataset", s3_output)
            logger.info(f"Data from table {table_name} successfully saved to {s3_output}")

        except Exception as e:
            logger.error(f"Failed to query and save data for table {table_name}: {e}")

class Ingestor:
    """
    Manages the data ingestion operations.
    """

    def __init__(self, data_manager: DataManager):
        """
        Initializes Ingestor with DataManager.
        Args:
            data_manager (DataManager): Instance of DataManager to handle data operations.
        """
        self.data_manager = data_manager

    def ingest_all_tables(self):
        """
        Ingests all tables defined in the tables list.
        """
        for table in tables:
            try:
                logger.info(f"Starting ingestion for table {table}")
                self.data_manager.query_and_save_to_s3(table)
                logger.info(f"Finished ingestion for table {table}")
            except Exception as e:
                logger.error(f"Failed to ingest table {table}: {e}")

if __name__ == "__main__":
    try:
        aws_manager = AWSManager(aws_region, aws_access_key_id, aws_secret_access_key)
        data_manager = DataManager(aws_manager)
        ingestor = Ingestor(data_manager)

        ingestor.ingest_all_tables()

    except Exception as e:
        logger.error(f"An error occurred during the ingestion process: {e}")
