import logging
import os

from pyspark.sql import SparkSession


logger = logging.getLogger(__name__)

"""
    Create and configure Spark session for:
    - Reading Parquet data from MinIO
    - Writing data to PostgreSQL
"""
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
        .appName("sp500-postgres-loader")

        # Local Spark configuration
        .master("local[*]")

        # MinIO / S3A configuration
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")

        # Spark performance
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.sql.shuffle.partitions", "12")

        .config("spark.driver.memory", "3g")

        .config("spark.driver.extraClassPath", "/opt/spark/jars/*")
        .config("spark.executor.extraClassPath", "/opt/spark/jars/*")

        .getOrCreate()
    )

    logger.info("Spark session created successfully. Version: %s", spark.version)

    return spark


def stop_spark_session(spark):
    if spark is not None:
        spark.stop()
        logger.info("Spark session stopped")