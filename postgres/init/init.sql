-- POSTGRESQL INITIALIZATION

-- TABLE 1: PROCESSED STOCK DATA
CREATE TABLE IF NOT EXISTS processed_stock_data (
    id BIGSERIAL PRIMARY KEY,
    trading_date DATE NOT NULL,
    ticker VARCHAR(20) NOT NULL,

    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    volume BIGINT,

    dividends DOUBLE PRECISION,
    stock_splits DOUBLE PRECISION,

    daily_return DOUBLE PRECISION,
    moving_average_7 DOUBLE PRECISION,
    moving_average_30 DOUBLE PRECISION,
    volatility_7 DOUBLE PRECISION,
    volatility_30 DOUBLE PRECISION,
    volume_change BIGINT,
    cumulative_return DOUBLE PRECISION,

    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,

    price_range DOUBLE PRECISION,
    price_change DOUBLE PRECISION,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 2: MONTHLY METRICS
CREATE TABLE IF NOT EXISTS monthly_metrics (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    average_close DOUBLE PRECISION,
    average_volume DOUBLE PRECISION,
    monthly_return DOUBLE PRECISION,
    volatility DOUBLE PRECISION,
    batch_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLE 3: QUARTERLY METRICS
CREATE TABLE IF NOT EXISTS quarterly_metrics (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    average_close DOUBLE PRECISION,
    average_volume DOUBLE PRECISION,
    quarterly_return DOUBLE PRECISION,
    volatility DOUBLE PRECISION,
    batch_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UNIQUE INDEX
CREATE UNIQUE INDEX IF NOT EXISTS idx_processed_date_ticker_batch
ON processed_stock_data (trading_date, ticker);

-- PERFORMANCE INDEXES
CREATE INDEX IF NOT EXISTS idx_processed_ticker
ON processed_stock_data (ticker);

CREATE INDEX IF NOT EXISTS idx_processed_date
ON processed_stock_data (trading_date);

CREATE INDEX IF NOT EXISTS idx_monthly_ticker
ON monthly_metrics (ticker);

CREATE INDEX IF NOT EXISTS idx_quarterly_ticker
ON quarterly_metrics (ticker);