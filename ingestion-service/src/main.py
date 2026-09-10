import os
import csv
import json
import logging

from pathlib import Path

from constants import Constants

from batch import generate_batch_id
from metadata import generate_metadata
from data_lake_controller import upload_to_minio

from dotenv import load_dotenv


# LOGGING CONFIGURATION
logging.basicConfig(level=logging.INFO, format=Constants.LOG_FORMAT)
logger = logging.getLogger(__name__)

# LOAD ENVIRONMENT VARIABLES
load_dotenv()

# FILE VALIDATION
def validate_file(file_path: str) -> None:
    """
    Vérifie que le fichier existe et n'est pas vide.
    """

    path = Path(file_path)
    if not path.exists():
        logger.error("Dataset file not found: %s", file_path)
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    if not path.is_file():
        logger.error("%s is not a file", file_path)
        raise ValueError(f"{file_path} is not a valid file")

    file_size = path.stat().st_size
    if file_size == 0:
        logger.error("Dataset file is empty")
        raise ValueError("Dataset file is empty")

    logger.info("Dataset file found")
    logger.info("Dataset size: %.2f MB", file_size / (1024 * 1024))

# SCHEMA VALIDATION
def validate_schema(file_path: str) -> None:
    """
    Vérifie que les colonnes du CSV correspondent
    exactement au schéma attendu.
    """

    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)

    logger.info("CSV columns detected:")
    logger.info(header)

    if header != Constants.EXPECTED_SP_500_COLUMNS:
        logger.error("Invalid CSV schema")
        logger.error("Expected columns: %s", Constants.EXPECTED_SP_500_COLUMNS)
        logger.error("Detected columns: %s", header)

        raise ValueError("CSV schema does not match expected schema")

    logger.info("CSV schema validation successful")

# MAIN
def main():
    logger.info("Starting S&P 500 ingestion service")
    dataset_path = os.getenv("SP_500_DATA_PATH", "./data/sp500_stock_data.csv")
    logger.info("Dataset path: %s", dataset_path)
    validate_file(dataset_path)
    validate_schema(dataset_path)
    batch_id = generate_batch_id()
    logger.info("Generated batch ID: %s", batch_id)

    metadata = generate_metadata(dataset_path, batch_id)
    logger.info(json.dumps(metadata, indent=4))
    upload_to_minio(dataset_path, metadata)

    logger.info("Ingestion validation completed successfully")


if __name__ == "__main__":
    main()