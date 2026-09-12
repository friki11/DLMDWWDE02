import logging

from pyspark.sql import functions as f


logger = logging.getLogger(__name__)

def standardize_column_names(dataframe):
    logger.info("Standardizing column names")

    column_mapping = {
        "Date": "trading_date",
        "Ticker": "ticker",
        "Adj Close": "adj_close",
        "Close": "close_price",
        "Dividends": "dividends",
        "High": "high_price",
        "Low": "low_price",
        "Open": "open_price",
        "Stock Splits": "stock_splits",
        "Volume": "volume",
    }

    for old_name, new_name in column_mapping.items():
        dataframe = dataframe.withColumnRenamed(old_name, new_name)

    return dataframe

def convert_date(dataframe):
    logger.info("Converting date column")

    return dataframe.withColumn(
        "trading_date",
        f.to_date(f.col("trading_date"), "yyyy-MM-dd")
    )

def count_invalid_dates(dataframe):
    invalid_dates = (
        dataframe
        .filter(f.col("trading_date").isNull())
        .count()
    )
    logger.info("Invalid dates found: %s", invalid_dates)

    return invalid_dates

def identify_invalid_records(dataframe):
    logger.info("Identifying invalid market records")

    invalid_records = (
        dataframe
        .filter(
            f.col("trading_date").isNull() |
            f.col("ticker").isNull() |
            f.col("open_price").isNull() |
            f.col("high_price").isNull() |
            f.col("low_price").isNull() |
            f.col("close_price").isNull() |
            (f.col("volume") <= 0)
        )
    )

    return invalid_records

def remove_invalid_records(dataframe):
    logger.info("Removing invalid records")

    clean_dataframe = (
        dataframe
        .filter(f.col("trading_date").isNotNull())
        .filter(f.col("ticker").isNotNull())
        .filter(f.col("open_price").isNotNull())
        .filter(f.col("high_price").isNotNull())
        .filter(f.col("low_price").isNotNull())
        .filter(f.col("close_price").isNotNull())
        .filter(f.col("volume") > 0)
    )

    return clean_dataframe

def remove_duplicates(dataframe):
    logger.info("Removing duplicates based on date and ticker")

    clean_dataframe = dataframe.dropDuplicates([
        "trading_date",
        "ticker",
    ])

    return clean_dataframe

def clean_data(dataframe):
    logger.info("Starting data cleaning")

    initial_count = dataframe.count()
    logger.info("Initial row count: %s", initial_count)
    dataframe = standardize_column_names(dataframe)
    dataframe = convert_date(dataframe)
    invalid_records = identify_invalid_records(dataframe)
    invalid_count = invalid_records.count()
    dataframe = remove_invalid_records(dataframe)
    dataframe = remove_duplicates(dataframe)
    final_count = dataframe.count()
    removed_records = initial_count - final_count

    logger.info("Invalid row count: %s", invalid_count)
    logger.info("Final row count: %s", final_count)
    logger.info("Removed records: %s", removed_records)
    logger.info("Data cleaning completed successfully")

    return dataframe