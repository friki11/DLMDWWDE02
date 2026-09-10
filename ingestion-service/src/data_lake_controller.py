import os
import logging
import json

from constants import Constants
from client_minio import get_minio_client


# LOGGING CONFIGURATION
logging.basicConfig(level=logging.INFO, format=Constants.LOG_FORMAT)
logger = logging.getLogger(__name__)


def upload_to_minio(file_path: str, metadata: dict) -> None:
    client = get_minio_client()

    bucket_name = os.getenv("MINIO_BUCKET")
    if not bucket_name:
        raise ValueError("MINIO_BUCKET environment variable is missing")

    batch_id = metadata["batch_id"]
    source_file = metadata["source_file"]

    # Structure du Data Lake
    csv_object_key = f"raw/{batch_id}/{source_file}"
    metadata_object_key = f"raw/{batch_id}/metadata.json"
    logger.info("Uploading dataset to MinIO...")
    logger.info("Bucket: %s",bucket_name)
    logger.info("Object: %s",csv_object_key)

    # Upload du fichier CSV
    client.upload_file(file_path, bucket_name, csv_object_key)

    logger.info("Dataset uploaded successfully")
    metadata_json = json.dumps(metadata, indent=4)

    client.put_object(
        Bucket=bucket_name,
        Key=metadata_object_key,
        Body=metadata_json.encode("utf-8"),
        ContentType="application/json"
    )

    logger.info("Metadata uploaded successfully")