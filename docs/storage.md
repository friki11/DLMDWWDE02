# Storage-Architektur

## MinIO Data Lake

MinIO wird als S3-kompatibler Data Lake eingesetzt.

Der Processing Service verwendet das S3A-Protokoll, um auf die Daten zuzugreifen.

## RAW Layer

```text
s3a://sp500-data-lake/raw/
```

Enthält die ursprünglichen Rohdaten.

## Clean Layer

```text
s3a://sp500-data-lake/processed/clean/
```

Enthält die bereinigten Daten.

Format:

```text
Parquet
```

## Feature Layer

```text
s3a://sp500-data-lake/processed/features/
```

Enthält die um zusätzliche Features angereicherten Daten.

## ML Layer

### Training

```text
s3a://sp500-data-lake/ml/train/
```

### Validierung

```text
s3a://sp500-data-lake/ml/validation/
```

### Test

```text
s3a://sp500-data-lake/ml/test/
```

## PostgreSQL Serving Layer

PostgreSQL wird verwendet, um die Daten für die API bereitzustellen.

Die Daten werden in Tabellen und Views organisiert.

Beispiele:

```text
processed_stock_data
```

## Datenformat

Für die transformierten Datensätze wird das Parquet-Format verwendet.
