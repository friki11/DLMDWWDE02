import logging
import os
import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


app = FastAPI(
    title="S&P 500 Data API",
    description="API for S&P 500 market data and ML features",
    version="1.0.0"
)

def get_database_connection():
    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "sp500_db"),
        user=os.getenv("POSTGRES_USER", "sp500_admin"),
        password=os.getenv("POSTGRES_PASSWORD", "Password"),
        cursor_factory=RealDictCursor,
    )

    return connection

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "sp500-api"
    }

@app.get("/tickers")
def get_tickers():
    connection = get_database_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT DISTINCT ticker
            FROM processed_stock_data
            ORDER BY ticker
            """
        )

        results = cursor.fetchall()

        return results

    finally:
        connection.close()

@app.get("/tickers/{ticker}")
def get_ticker(ticker: str, limit: int = 50):
    connection = get_database_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                ticker,
                trading_date,
                close_price,
                daily_return,
                moving_average_7,
                moving_average_30,
                volatility_7,
                volatility_30,
                volume_change,
                target_direction

            FROM processed_stock_data

            WHERE ticker = %s
            LIMIT %s
            """,
            (ticker.upper(), limit)
        )

        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Ticker not found")

        return result

    finally:
        connection.close()

@app.get("/tickers/{ticker}/history")
def get_ticker_history(ticker: str, limit: int = 50):
    connection = get_database_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                ticker,
                trading_date,
                close_price,
                daily_return,
                moving_average_7,
                moving_average_30,
                volatility_7,
                volatility_30,
                volume_change,
                target_direction

            FROM processed_stock_data

            WHERE ticker = %s

            ORDER BY trading_date DESC

            LIMIT %s
            """,
            (ticker.upper(), limit)
        )

        results = cursor.fetchall()

        return results
    finally:
        connection.close()