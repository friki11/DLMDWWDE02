import logging
import os

from pyspark.sql import SparkSession
from schema import SP500_SCHEMA


logger = logging.getLogger(__name__)


# CREATE SPARK SESSION
def create_spark_session():
    logger.info("Creating Spark session")
    minio_endpoint = os.getenv("MINIO_ENDPOINT")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY")
    if not all([minio_endpoint, minio_access_key, minio_secret_key]):
        raise ValueError("Environment variables are not set")

    spark = (
        SparkSession
        .builder
        .appName("sp500-processing-service")
        .master("local[*]")

        # S3A CONFIGURATION
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

        .config("spark.driver.extraClassPath", "/opt/spark/jars/*")
        .config("spark.executor.extraClassPath", "/opt/spark/jars/*")

        .config("spark.driver.memory", "3g")
        .config("spark.block.size", "67108864")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.memory.offHeap.enabled", "true")
        .config("spark.memory.offHeap.size", "2g")

        .getOrCreate()
    )

    logger.info("Spark session created successfully")

    return spark

# READ RAW DATA
def read_raw_data(spark):
    bucket_name = os.getenv("MINIO_BUCKET")
    if not bucket_name:
        raise ValueError("Environment variables are not set")

    raw_data_path = f"s3a://{bucket_name}/raw/"
    logger.info("Reading RAW data from: %s", raw_data_path)
    dataframe = (
        spark
        .read
        .option("header", "true")
        .option("recursiveFileLookup", "true")
        .option("delimiter", ",")
        .option("quote", '"')
        .option("escape", '"')
        .option("pathGlobFilter", "*.csv")
        .schema(SP500_SCHEMA)
        .csv(raw_data_path)
    )

    logger.info("RAW data loaded successfully")

    return dataframe

# DATASET INFORMATION
def display_dataset_information(dataframe):
    #logger.info("Number of rows: %s", dataframe.count())
    #logger.info("Number of columns: %s", len(dataframe.columns))
    logger.info("Columns: %s", dataframe.columns)
    logger.info("Dataset schema:")
    dataframe.printSchema()