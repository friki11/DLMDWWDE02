import logging
import json

from botocore.exceptions import ClientError
from constants import Constants

# LOGGING CONFIGURATION
logging.basicConfig(level=logging.INFO, format=Constants.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Checks if a file with the same checksum has already been ingested.
def check_existing_ingestion(client, bucket_name: str, checksum: str) -> bool:
    registry_key = f"ingestion_registry/{checksum}.json"
    try:
        client.head_object(Bucket=bucket_name, Key=registry_key),
        logger.warning("Dataset already ingested")
        logger.warning("Checksum: %s", checksum)

        return True
    except ClientError as error:
        error_code = error.response["Error"].get("Code")
        if error_code in ["404", "NoSuchKey", "NotFound"]:
            logger.info("Dataset not previously ingested")

            return False

        raise


# Create a registry to identify files that have already been ingested.
def create_ingestion_registry(client, bucket_name: str, metadata: dict) -> None:
    checksum = metadata["file_checksum_sha256"]
    registry_key = f"ingestion_registry/{checksum}.json"
    registry_data = {
        "batch_id": metadata["batch_id"],
        "checksum": checksum,
        "source_file": metadata["source_file"],
        "ingestion_timestamp": metadata["ingestion_timestamp"]
    }

    registry_json = json.dumps(registry_data, indent=4)
    client.put_object(
        Bucket=bucket_name,
        Key=registry_key,
        Body=registry_json.encode("utf-8"),
        ContentType="application/json"
    )
    logger.info("Ingestion registry created successfully")


# Checks that the bucket exists. Creates it automatically if it does not exist.
def ensure_bucket_exists(client, bucket_name: str) -> None:
    try:
        client.head_bucket(Bucket=bucket_name)
        logger.info("Bucket already exists: %s", bucket_name)
    except ClientError as error:
        error_code = error.response["Error"].get("Code")
        if error_code in ["404", "NoSuchBucket", "NotFound"]:
            logger.info("Creating bucket: %s", bucket_name)
            client.create_bucket(Bucket=bucket_name)
            logger.info("Bucket created successfully")
        else:
            logger.error("Error checking bucket: %s", error)

            raise