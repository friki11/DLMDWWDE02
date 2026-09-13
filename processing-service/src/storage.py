import logging
import os

logger = logging.getLogger(__name__)

bucket_name = os.getenv("MINIO_BUCKET")
if bucket_name is None:
    raise ValueError("Please set environment variable MINIO_BUCKET")

CLEAN_PATH = f"s3a://{bucket_name}/processed/clean/"
FEATURES_PATH = f"s3a://{bucket_name}/processed/features/"

ML_TRAIN_PATH = f"s3a://{bucket_name}/ml/train/"
ML_VALIDATION_PATH = f"s3a://{bucket_name}/ml/validation/"
ML_TEST_PATH = f"s3a://{bucket_name}/ml/test/"

def write_parquet(dataframe, path, dataset_name, partitions=12):
    logger.info("Preparing to save dataset: %s", dataset_name)

    dataframe = dataframe.repartition(partitions)
    logger.info("Writing %s using %s partitions", dataset_name, partitions)

    (
        dataframe
        .write
        .mode("overwrite")
        .option("compression", "snappy")
        .parquet(path)
    )

    logger.info("%s successfully saved to: %s", dataset_name, path)

def save_clean_data(dataframe):
    logger.info("Saving clean data to MinIO")

    write_parquet(
        dataframe=dataframe,
        path=CLEAN_PATH,
        dataset_name="Clean dataset",
        partitions=12
    )

def save_feature_data(dataframe):
    logger.info("Saving feature data to MinIO")

    write_parquet(
        dataframe=dataframe,
        path=FEATURES_PATH,
        dataset_name="Feature dataset",
        partitions=12
    )

def save_ml_datasets(train_dataframe, validation_dataframe, test_dataframe):
    logger.info("Saving ML datasets")

    write_parquet(
        dataframe=train_dataframe,
        path=ML_TRAIN_PATH,
        dataset_name="ML train dataset",
        partitions=8
    )

    write_parquet(
        dataframe=validation_dataframe,
        path=ML_VALIDATION_PATH,
        dataset_name="ML validation dataset",
        partitions=4
    )

    write_parquet(
        dataframe=test_dataframe,
        path=ML_TEST_PATH,
        dataset_name="ML test dataset",
        partitions=4
    )

    logger.info("ML datasets successfully saved")

def save_processed_data(clean_dataframe, feature_dataframe, train_dataframe, validation_dataframe, test_dataframe):
    logger.info("Starting data storage")

    save_clean_data(clean_dataframe)
    save_feature_data(feature_dataframe)
    save_ml_datasets(train_dataframe, validation_dataframe, test_dataframe)

    logger.info("Data storage completed successfully")