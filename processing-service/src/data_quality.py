import logging

from pyspark.sql import functions as f


logger = logging.getLogger(__name__)

def check_null_values(dataframe):
    logger.info("Checking null values")

    null_counts = dataframe.select([
        f.sum(f.col(column).isNull().cast("int")).alias(column)
        for column in dataframe.columns
    ])
    null_counts.show(truncate=False)

    return null_counts

def check_duplicates(dataframe):
    logger.info("Checking duplicate rows")

    total_rows = dataframe.count()
    distinct_rows = dataframe.distinct().count()
    duplicate_rows = total_rows - distinct_rows
    logger.info("Duplicate rows: %s", duplicate_rows)

    duplicate_ticker_date = (
        dataframe
        .groupBy("Date", "Ticker")
        .count()
        .filter(f.col("count") > 1)
        .count()
    )

    logger.info("Duplicate Date + Ticker combinations: %s", duplicate_ticker_date)

    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_ticker_date": duplicate_ticker_date,
    }

def check_negative_values(dataframe):
    logger.info("Checking negative values")

    numeric_columns = [
        "Adj Close",
        "Close",
        "Dividends",
        "High",
        "Low",
        "Open",
        "Volume",
    ]

    results = {}
    for column in numeric_columns:
        negative_count = (
            dataframe
            .filter(f.col(column) < 0)
            .count()
        )
        results[column] = negative_count
        logger.info("Negative values in %s: %s", column, negative_count)

    return results

def check_ohlc_consistency(dataframe):
    logger.info("Checking OHLC consistency")

    inconsistent_rows = (
        dataframe
        .filter(
            (f.col("High") < f.col("Low")) |
            (f.col("High") < f.col("Open")) |
            (f.col("High") < f.col("Close")) |
            (f.col("Low") > f.col("Open")) |
            (f.col("Low") > f.col("Close"))
        )
        .count()
    )

    logger.info("Inconsistent OHLC rows: %s", inconsistent_rows)

    return inconsistent_rows

def check_tickers(dataframe):
    logger.info("Checking tickers")

    ticker_count = (
        dataframe
        .select("Ticker")
        .distinct()
        .count()
    )

    logger.info("Number of unique tickers: %s", ticker_count)

    return ticker_count

def run_data_quality_checks(dataframe):
    logger.info("Starting Data Quality checks")

    check_null_values(dataframe)
    check_duplicates(dataframe)
    check_negative_values(dataframe)
    check_ohlc_consistency(dataframe)
    check_tickers(dataframe)
    logger.info("Data Quality checks completed")