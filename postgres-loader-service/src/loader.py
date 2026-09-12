import logging
import os
import psycopg2

from pyspark.sql import functions as f


logger = logging.getLogger(__name__)

"""
    Read feature data from MinIO.
"""
def read_feature_data(spark):
    bucket_name = os.getenv("MINIO_BUCKET")

    features_path = f"s3a://{bucket_name}/processed/features/"
    logger.info("Reading feature data from: %s", features_path)
    dataframe = spark.read.parquet(features_path)
    logger.info("Feature data loaded successfully")
    logger.info("Number of partitions: %s", dataframe.rdd.getNumPartitions())

    return dataframe

"""
    Select and prepare data for PostgreSQL Serving Layer.
"""
def prepare_serving_data(dataframe):
    logger.info("Preparing data for PostgreSQL")

    serving_dataframe = dataframe.select(
        # Identification
        "trading_date",
        "ticker",

        # Market data
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adj_close",
        "volume",

        # Financial events
        "dividends",
        "stock_splits",

        # Engineered features
        "daily_return",
        "moving_average_7",
        "moving_average_30",
        "volatility_7",
        "volatility_30",
        "volume_change",
        "cumulative_return",

        # Time features
        "year",
        "month",
        "day_of_week",
    )

    logger.info("Serving dataset columns: %s", serving_dataframe.columns)

    return serving_dataframe

"""
    Control the number of partitions before JDBC writing.

    PostgreSQL should not receive too many
    simultaneous JDBC connections.
"""
def optimize_partitions(dataframe):
    logger.info("Optimizing partitions for PostgreSQL")

    dataframe = dataframe.repartition(8)
    logger.info("Number of partitions after optimization: %s", dataframe.rdd.getNumPartitions())

    return dataframe

"""
    Remove existing data while preserving:
    - table structure
    - indexes
    - constraints
"""
def truncate_processed_stock_data():
    logger.info("Truncating PostgreSQL processed_stock_data table")

    postgres_host = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_database = os.getenv("POSTGRES_DB")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    if not all([postgres_host, postgres_port, postgres_database,]):
        raise ValueError("Environment variables are not set")

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host=postgres_host,
            port=postgres_port,
            database=postgres_database,
            user=postgres_user,
            password=postgres_password,
        )

        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE processed_stock_data RESTART IDENTITY;")
        connection.commit()
        logger.info("processed_stock_data table truncated successfully")

    except Exception as error:
        if connection is not None:
            connection.rollback()

        logger.exception("Failed to truncate processed_stock_data: %s", error)

        raise

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

"""
    Write Spark DataFrame to PostgreSQL using JDBC.
"""
def write_to_postgresql(dataframe):
    postgres_host = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_database = os.getenv("POSTGRES_DB")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    jdbc_url = (
        f"jdbc:postgresql://"
        f"{postgres_host}:"
        f"{postgres_port}/"
        f"{postgres_database}"
    )

    logger.info("Starting PostgreSQL data loading")

    (
        dataframe
        .write
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "processed_stock_data")
        .option("user", postgres_user)
        .option("password", postgres_password)
        .option("driver", "org.postgresql.Driver")
        .option("batchsize", "10000")
        .option("isolationLevel", "READ_COMMITTED")
        .mode("append")
        .save()
    )

    logger.info("Data successfully written to PostgreSQL")

"""
    Complete loading pipeline.
"""
def load_features_to_postgresql(spark):
    logger.info("Starting PostgreSQL loading pipeline")

    # Check PostgreSQL connection
    check_postgresql_connection()

    # Check table
    check_processed_stock_table()

    # Read data from MinIO
    dataframe = read_feature_data(spark)

    # Prepare serving data
    dataframe = prepare_serving_data(dataframe)

    # Optimize Spark partitions
    dataframe = optimize_partitions(dataframe)

    # Count records before loading
    spark_record_count = dataframe.count()

    logger.info("Spark records to load: %s", spark_record_count)

    # Remove previous data
    truncate_processed_stock_data()

    # Write data
    write_to_postgresql(dataframe)

    # Verify PostgreSQL record count
    postgresql_record_count = (get_postgresql_record_count())

    logger.info("PostgreSQL records loaded: %s", postgresql_record_count)

    # Validate loading
    if spark_record_count != postgresql_record_count:

        raise RuntimeError(
            "Record count mismatch: "
            f"Spark={spark_record_count}, "
            f"PostgreSQL={postgresql_record_count}"
        )

    logger.info("PostgreSQL record count validation successful")
    logger.info("PostgreSQL loading pipeline completed successfully")


"""
    Check PostgreSQL connectivity before loading data.
"""
def check_postgresql_connection():
    logger.info("Checking PostgreSQL connection")

    postgres_host = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_database = os.getenv("POSTGRES_DB")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    if not all([postgres_host, postgres_port, postgres_database]):
        raise ValueError("Environment variables are not set")

    connection = None
    try:
        connection = psycopg2.connect(
            host=postgres_host,
            port=postgres_port,
            database=postgres_database,
            user=postgres_user,
            password=postgres_password,
        )

        logger.info("PostgreSQL connection successful")
    except Exception as error:
        logger.exception("PostgreSQL connection failed: %s", error)

        raise
    finally:
        if connection is not None:
            connection.close()

def check_processed_stock_table():
    logger.info("Checking processed_stock_data table")

    postgres_host = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_database = os.getenv("POSTGRES_DB")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    if not all([postgres_host, postgres_port, postgres_database]):
        raise ValueError("Environment variables are not set")

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host=postgres_host,
            port=postgres_port,
            database=postgres_database,
            user=postgres_user,
            password=postgres_password,
        )

        cursor = connection.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'processed_stock_data'
            );
        """)

        table_exists = cursor.fetchone()[0]
        if not table_exists:
            raise RuntimeError("processed_stock_data table does not exist")

        logger.info("processed_stock_data table exists")
    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

def get_postgresql_record_count():
    postgres_host = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_database = os.getenv("POSTGRES_DB")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    if not all([postgres_host, postgres_port, postgres_database]):
        raise ValueError("Environment variables are not set")

    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host=postgres_host,
            port=postgres_port,
            database=postgres_database,
            user=postgres_user,
            password=postgres_password,
        )

        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM processed_stock_data;")
        record_count = cursor.fetchone()[0]

        return record_count
    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()