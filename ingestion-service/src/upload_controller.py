import os
import logging
import json

from constants import Constants
from client_minio import get_minio_client
from ingestion_controller import create_ingestion_registry, check_existing_ingestion, ensure_bucket_exists


# LOGGING CONFIGURATION
logging.basicConfig(level=logging.INFO, format=Constants.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Checks that the object exists in MinIO and that its size corresponds to the source file.
def verify_upload(client, bucket_name: str, object_key: str, expected_size: int) -> None:
    try:
        response = client.head_object(Bucket=bucket_name, Key=object_key)
        uploaded_size = response["ContentLength"]
        logger.info("Uploaded file size: %s bytes", uploaded_size)
        if uploaded_size != expected_size:
            raise ValueError(f"Upload verification failed. Expected {expected_size} bytes, got {uploaded_size} bytes.")

        logger.info("Upload verification successful")

    except Exception as error:
        raise Exception("Upload verification failed: %s", error)


def upload_to_minio(file_path: str, metadata: dict) -> None:
    client = get_minio_client()
    bucket_name = os.getenv("MINIO_BUCKET")
    if not bucket_name:
        raise ValueError("MINIO_BUCKET environment variable is missing")

    ensure_bucket_exists(client, bucket_name)

    checksum = metadata["file_checksum_sha256"]
    already_ingested = check_existing_ingestion(client=client, bucket_name=bucket_name, checksum=checksum)
    if already_ingested:
        logger.info("Was already ingested")

        return

    batch_id = metadata["batch_id"]
    source_file = metadata["source_file"]

    # Structure du Data Lake
    csv_object_key = f"raw/{batch_id}/{source_file}"
    metadata_object_key = f"raw/{batch_id}/metadata.json"
    logger.info("Uploading dataset to MinIO...")
    logger.info("Bucket: %s",bucket_name)
    logger.info("Object: %s",csv_object_key)

    # Upload CSV file
    client.upload_file(file_path, bucket_name, csv_object_key)
    # Verify uploaded dataset
    verify_upload(
        client=client,
        bucket_name=bucket_name,
        object_key=csv_object_key,
        expected_size=metadata["file_size_bytes"]
    )
    logger.info("Dataset uploaded successfully")
    metadata_json = json.dumps(metadata, indent=4)
    metadata_bytes = metadata_json.encode("utf-8")

    client.put_object(
        Bucket=bucket_name,
        Key=metadata_object_key,
        Body=metadata_bytes,
        ContentType="application/json"
    )

    # Verify metadata upload
    verify_upload(
        client=client,
        bucket_name=bucket_name,
        object_key=metadata_object_key,
        expected_size=len(metadata_bytes)
    )
    logger.info("Metadata uploaded successfully")

    # Create ingestion register
    create_ingestion_registry(client=client, bucket_name=bucket_name, metadata=metadata)
    logger.info("Ingestion completed successfully")