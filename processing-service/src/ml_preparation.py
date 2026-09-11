import logging

from pyspark.sql import functions as f
from pyspark.sql.window import Window


logger = logging.getLogger(__name__)

def create_ticker_window():
    window = (
        Window
        .partitionBy("ticker")
        .orderBy("date")
    )

    return window

def add_target_variable(dataframe):
    logger.info("Creating target variable")

    window = create_ticker_window()
    dataframe = dataframe.withColumn(
        "next_close",
        f.lead("close_price").over(window)
    )

    dataframe = dataframe.withColumn(
        "target_direction",
        f.when(f.col("next_close").isNull(), None)
        .when(
            f.col("next_close") > f.col("close_price"),
            1
        ).otherwise(0)
    )

    return dataframe

def check_ml_nulls(dataframe):
    logger.info("Checking NULL values before ML preparation")

    null_counts = dataframe.select([
        f.sum(
            f.col(column)
            .isNull()
            .cast("int")
        ).alias(column)
        for column in dataframe.columns
    ])
    null_counts.show(truncate=False)

def select_ml_columns(dataframe):
    logger.info("Selecting ML columns")

    ml_columns = [
        "trading_date",
        "ticker",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume",
        "daily_return",
        "moving_average_7",
        "moving_average_30",
        "volatility_7",
        "volatility_30",
        "volume_change",
        "year",
        "month",
        "day_of_week",
        "target_direction",
    ]

    dataframe = dataframe.select(ml_columns)

    return dataframe

def remove_incomplete_ml_records(dataframe):
    logger.info("Removing incomplete ML records")

    dataframe = dataframe.dropna(
        subset=[
            "daily_return",
            "moving_average_7",
            "moving_average_30",
            "volatility_7",
            "volatility_30",
            "volume_change",
            "target_direction",
        ]
    )

    return dataframe

def split_ml_dataset(dataframe):
    logger.info("Creating temporal Train Validation Test split")

    min_max_date = (
        dataframe
        .select(
            f.min("date").alias("min_date"),
            f.max("date").alias("max_date")
        )
        .collect()[0]
    )

    min_date = (min_max_date["min_date"])
    max_date = (min_max_date["max_date"])
    logger.info("Dataset minimum date: %s", min_date)

    logger.info(
        "Dataset maximum date: %s",
        max_date
    )

    return min_date, max_date

def create_temporal_splits(dataframe):
    logger.info("Creating temporal dataset splits")

    train_dataframe = (
        dataframe
        .filter(f.col("date") < f.lit("2020-01-01"))
    )

    validation_dataframe = (
        dataframe
        .filter(
            (f.col("date") >= f.lit("2020-01-01")) &
            (f.col("date") < f.lit("2023-01-01"))
        )
    )

    test_dataframe = (
        dataframe
        .filter(f.col("date") >= f.lit("2023-01-01"))
    )

    logger.info("Train records: %s", train_dataframe.count())
    logger.info("Validation records: %s", validation_dataframe.count())
    logger.info("Test records: %s", test_dataframe.count())

    return (
        train_dataframe,
        validation_dataframe,
        test_dataframe,
    )

def prepare_ml_data(dataframe):
    logger.info("Starting ML data preparation")

    dataframe = add_target_variable(dataframe)
    check_ml_nulls(dataframe)
    dataframe = select_ml_columns(dataframe)
    dataframe = remove_incomplete_ml_records(dataframe)
    train_dataframe, validation_dataframe, test_dataframe = create_temporal_splits(dataframe)
    logger.info("ML data preparation completed")

    return (
        train_dataframe,
        validation_dataframe,
        test_dataframe,
    )