import logging

from pyspark.sql import functions as f
from pyspark.sql.window import Window


logger = logging.getLogger(__name__)

def create_ticker_window():
    return (
        Window
        .partitionBy("ticker")
        .orderBy("trading_date")
    )

def add_daily_return(dataframe):
    logger.info("Adding daily return feature")

    window = create_ticker_window()
    dataframe = dataframe.withColumn("previous_close", f.lag("close_price").over(window))
    dataframe = dataframe.withColumn(
        "daily_return",
        f.when(
            f.col("previous_close") > 0,
            (f.col("close_price") - f.col("previous_close")) / f.col("previous_close")
        ).otherwise(None),
    )

    dataframe = dataframe.drop("previous_close")

    return dataframe

def add_moving_average_7(dataframe):
    logger.info("Adding 7-day moving average")

    window = (
        Window
        .partitionBy("ticker")
        .orderBy("trading_date")
        .rowsBetween(-6, 0)
    )

    dataframe = dataframe.withColumn("moving_average_7", f.avg("close_price").over(window))

    return dataframe

def add_moving_average_30(dataframe):
    logger.info("Adding 30-day moving average")

    window = (
        Window
        .partitionBy("ticker")
        .orderBy("trading_date")
        .rowsBetween(-29, 0)
    )

    dataframe = dataframe.withColumn("moving_average_30", f.avg("close_price").over(window))

    return dataframe

def add_volatility_7(dataframe):
    logger.info("Adding 7-day volatility")

    window = (
        Window
        .partitionBy("ticker")
        .orderBy("trading_date")
        .rowsBetween(-6, 0)
    )

    dataframe = dataframe.withColumn("volatility_7", f.stddev("daily_return").over(window))

    return dataframe

def add_volatility_30(dataframe):
    logger.info("Adding 30-day volatility")

    window = (
        Window
        .partitionBy("ticker")
        .orderBy("trading_date")
        .rowsBetween(-29, 0)
    )

    dataframe = dataframe.withColumn("volatility_30", f.stddev("daily_return").over(window))

    return dataframe

def add_volume_change(dataframe):
    logger.info("Adding volume change feature")

    window = create_ticker_window()
    dataframe = dataframe.withColumn("previous_volume", f.lag("volume").over(window))
    dataframe = dataframe.withColumn(
        "volume_change",
        f.when(
            f.col("previous_volume") > 0,
            (f.col("volume") - f.col("previous_volume")) / f.col("previous_volume")
        ).otherwise(None),
    )

    dataframe = dataframe.drop("previous_volume")

    return dataframe

def add_time_features(dataframe):
    logger.info("Adding time features")

    dataframe = dataframe.withColumn("year", f.year("trading_date"))
    dataframe = dataframe.withColumn("month", f.month("trading_date"))
    dataframe = dataframe.withColumn("day_of_week", f.dayofweek("trading_date"))

    return dataframe

def add_cumulative_return(dataframe):
    logger.info("Adding cumulative return")

    window = (
        Window
        .partitionBy("ticker")
        .orderBy("trading_date")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    dataframe = dataframe.withColumn("first_close", f.first("close_price").over(window))
    dataframe = dataframe.withColumn(
        "cumulative_return",
        f.when(
            f.col("first_close") > 0,
            (f.col("close_price") - f.col("first_close")) / f.col("first_close")
        ).otherwise(None),
    )

    dataframe = dataframe.drop("first_close")

    return dataframe

def create_features(dataframe):
    logger.info("Starting feature engineering")

    dataframe = add_daily_return(dataframe)
    dataframe = add_moving_average_7(dataframe)
    dataframe = add_moving_average_30(dataframe)
    dataframe = add_volatility_7(dataframe)
    dataframe = add_volatility_30(dataframe)
    dataframe = add_volume_change(dataframe)
    dataframe = add_time_features(dataframe)
    dataframe = add_cumulative_return(dataframe)
    logger.info("Feature engineering completed successfully")


    return dataframe