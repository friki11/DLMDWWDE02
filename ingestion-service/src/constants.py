class Constants:
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    # EXPECTED DATASET SCHEMA
    EXPECTED_SP_500_COLUMNS = [
        "Date",
        "Ticker",
        "Adj Close",
        "Close",
        "Dividends",
        "High",
        "Low",
        "Open",
        "Stock Splits",
        "Volume",
    ]