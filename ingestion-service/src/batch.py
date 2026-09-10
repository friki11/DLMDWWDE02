import uuid

from datetime import datetime, timezone

# Generates a unique identifier for each ingestion.
def generate_batch_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime( "%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"batch_{timestamp}_{unique_id}"