from pathlib import Path
from datetime import datetime, timezone
from checksum import  calculate_checksum
from constants import Constants

# Generates metadata associated with an ingestion.
def generate_metadata( file_path: str, batch_id: str) -> dict:
    path = Path(file_path)

    return {
        "batch_id": batch_id,
        "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
        "source_file": path.name,
        "file_size_bytes": path.stat().st_size,
        "file_checksum_sha256": calculate_checksum(file_path),
        "expected_columns": Constants.EXPECTED_SP_500_COLUMNS,
        "pipeline_type": "batch",
        "dataset": "sp500_stock_data",
    }