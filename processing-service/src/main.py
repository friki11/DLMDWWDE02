import logging

from spark_controller import create_spark_session, display_dataset_information, read_raw_data
from data_quality import run_data_quality_checks
from cleaning import clean_data
from feature_engineering import create_features
from ml_preparation import prepare_ml_data


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting S&P 500 processing service")
    spark = None
    try:
        spark = create_spark_session()
        logger.info("Spark version: %s", spark.version)
        dataframe = read_raw_data(spark)
        display_dataset_information(dataframe)
        run_data_quality_checks(dataframe)
        clean_dataframe = clean_data(dataframe)
        logger.info("Clean dataset row count: %s", clean_dataframe.count())
        featured_dataframe = create_features(clean_dataframe)
        logger.info("Feature dataset row count: %s", featured_dataframe.count())
        train_dataframe, validation_dataframe, test_dataframe = prepare_ml_data(featured_dataframe)
        logger.info("ML datasets created successfully")
        """featured_dataframe.select(
            "trading_date",
            "ticker",
            "close_price",
            "daily_return",
            "moving_average_7",
            "moving_average_30",
            "volatility_7",
            "volatility_30",
            "volume_change",
            "cumulative_return",
        ).show(20, truncate=False)"""
        logger.info("Processing service completed successfully")
    except Exception as error:
        logger.exception("Processing service failed: %s", error)

        raise
    finally:
        if spark is not None:
            spark.stop()
            logger.info("Spark session stopped")

if __name__ == "__main__":
    main()