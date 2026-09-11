from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    LongType,
)

SP500_SCHEMA = StructType([
    StructField("Date", StringType(), nullable=False),
    StructField("Ticker", StringType(), nullable=False),
    StructField("Adj Close", DoubleType(), nullable=True),
    StructField("Close", DoubleType(), nullable=True),
    StructField("Dividends", DoubleType(), nullable=True),
    StructField("High", DoubleType(), nullable=True),
    StructField("Low", DoubleType(), nullable=True),
    StructField("Open", DoubleType(), nullable=True),
    StructField("Stock Splits", DoubleType(), nullable=True),
    StructField("Volume", LongType(), nullable=True),
])
