import logging

from spark_controller import (create_spark_session, stop_spark_session,)
from loader import load_features_to_postgresql


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting S&P 500 PostgreSQL Loader Service")

    spark = None
    try:
        # Create Spark session
        spark = create_spark_session()
        logger.info("Spark version: %s", spark.version)

        # Load features into PostgreSQL
        load_features_to_postgresql(spark)
        logger.info("PostgreSQL Loader Service completed successfully")
    except Exception as error:
        logger.exception("PostgreSQL Loader Service failed: %s", error)

        raise

    finally:
        if spark is not None:
            stop_spark_session(spark)
            logger.info("Spark session stopped")


if __name__ == "__main__":
    main()