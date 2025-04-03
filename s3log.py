import logging
import boto3
from dotenv import load_dotenv
import os

class S3Handler(logging.Handler):
    def __init__(self, access_key, secret_key, bucket_name, logfile,  region_name='us-east-1'):
        super().__init__()
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )
        self.logfile = logfile
        self.level = logging.DEBUG
        self.bucket_name = bucket_name
        self.lock = self.createLock()
        self.filters = []

    def emit(self, record):
        try:
            # Format the log entry
            log_entry = self.format(record)

            # Try to retrieve the existing log file from S3
            try:
                response = self.client.get_object(Bucket=self.bucket_name, Key=self.logfile)
                existing_logs = response['Body'].read().decode('utf-8')
            except self.client.exceptions.NoSuchKey:
                # If the file doesn't exist, start with an empty string
                existing_logs = ""

            # Append the new log entry to the existing logs
            updated_logs = existing_logs + log_entry + '\n'

            # Upload the updated logs back to S3
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=self.logfile,
                Body=updated_logs,
                ContentType='text/plain'
            )
        except Exception as ex:
            print(f"Failed to log to S3: {ex}")




# Load environment variables from the .env file
load_dotenv()

# Access AWS credentials and region from the environment
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

# Create a logger
logger = logging.getLogger(__name__)

s3handler = S3Handler(aws_access_key, aws_secret_key, 's3logtestadidaw', 'logfile.log', region_name=aws_region)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
s3handler.setFormatter(formatter)
logger.addHandler(s3handler)

logger.setLevel(logging.DEBUG)

logger.debug("Let's do something")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")

# logger.setLevel(logging.DEBUG)

# # Create a console handler and set its level
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)

# # Create a formatter and add it to the handler

# # Add the handler to the logger
# logger.addHandler(console_handler)

# logger.debug("Let's do something")

