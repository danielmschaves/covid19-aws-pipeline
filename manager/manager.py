import boto3
import awswrangler as wr

class AWSManager:
    """
    Manages AWS credentials and operations.
    """

    def __init__(
        self,
        aws_region: str,
        aws_access_key: str,
        aws_secret_access_key: str,
    ):
        """
        Initializes AWSManager.

        Args:
            aws_region (str): AWS region.
            aws_access_key (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
        """
        self.aws_region = aws_region
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = aws_secret_access_key
        self.s3_client = self.create_s3_client(aws_region, aws_access_key, aws_secret_access_key)
        self.athena_client = self.create_athena_client(aws_region, aws_access_key, aws_secret_access_key)
        self.load_credentials(aws_region, aws_access_key, aws_secret_access_key)

    def create_s3_client(self, aws_region: str, aws_access_key: str, aws_secret_access_key: str):
        """
        Creates a boto3 S3 client with the given credentials.

        Args:
            aws_region (str): AWS region.
            aws_access_key (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.

        Returns:
            boto3.client: Configured boto3 S3 client.
        """
        return boto3.client(
            's3',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key
        )

    def create_athena_client(self, aws_region: str, aws_access_key: str, aws_secret_access_key: str):
        """
        Creates a boto3 Athena client with the given credentials.

        Args:
            aws_region (str): AWS region.
            aws_access_key (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.

        Returns:
            boto3.client: Configured boto3 Athena client.
        """
        return boto3.client(
            'athena',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key
        )
    
    def load_credentials(self, aws_region: str, aws_access_key: str, aws_secret_access_key: str):
        """
        Loads AWS credentials for AWS Wrangler.

        Args:
            aws_region (str): AWS region.
            aws_access_key (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
        """
        wr.config.s3_endpoint_url = f'https://s3.{aws_region}.amazonaws.com'
        wr.config.region_name = aws_region
        wr.config.aws_access_key_id = aws_access_key
        wr.config.aws_secret_access_key = aws_secret_access_key

    def query_athena_to_s3(self, sql_query: str, database: str, s3_output: str):
        """
        Queries Athena and stores the result in S3 as a Parquet file.

        Args:
            sql_query (str): SQL query to execute on Athena.
            database (str): Athena database name.
            s3_output (str): S3 path to store the output Parquet file.
        """
        # Run the Athena query and store the result in a Pandas DataFrame
        df = wr.athena.read_sql_query(sql=sql_query, database=database)
        
        # Write the DataFrame to S3 as Parquet
        wr.s3.to_parquet(
            df=df,
            path=s3_output,
            dataset=True,
            mode="overwrite"
        )
