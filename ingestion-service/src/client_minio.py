import boto3
import logging
import os

from constants import Constants

# LOGGING CONFIGURATION
logging.basicConfig(level=logging.INFO, format=Constants.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Crée un client compatible S3 pour MinIO.
def get_minio_client():
    endpoint = os.getenv("MINIO_ENDPOINT")
    if not endpoint:
        raise ValueError("MINIO_ENDPOINT environment variable is missing")

    access_key = os.getenv("MINIO_ROOT_USER")
    if not access_key:
        raise ValueError("MINIO_ROOT_USER environment variable is missing")

    secret_key = os.getenv("MINIO_ROOT_PASSWORD")
    if not secret_key:
        raise ValueError("MINIO_ROOT_PASSWORD environment variable is missing")

    logger.info("Connecting to MinIO endpoint: %s", endpoint)

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1"
    )