# Datenpipeline

## Ziel

Die Pipeline ermöglicht es, Rohdaten des Aktienmarktes in Datensätze umzuwandeln, die für Analysen, Machine Learning und die Bereitstellung über eine API geeignet sind.

## Schritt 1 — Quelldaten

Der Datensatz enthält historische Daten für mehrere Unternehmen des S&P 500.

Wichtige Spalten:

```text
Date

Ticker

Adj Close

Close

Dividends

High

Low

Open

Stock Splits

Volume
```

## Schritt 2 — Data Ingestion

Der Datensatz wird in MinIO geladen.

Ziel:

```text
s3a://sp500-data-lake/raw/
```

Der ursprüngliche Datensatz wird unverändert gespeichert.

## Schritt 3 — Data Quality

Vor jeder Transformation werden mehrere Qualitätsprüfungen durchgeführt:

* Überprüfung auf NULL-Werte.
* Überprüfung auf Duplikate.
* Überprüfung auf negative Werte.
* Überprüfung der Konsistenz.

## Schritt 4 — Data Cleaning

Anschließend werden die Daten bereinigt.

Die Verarbeitung umfasst:

* Standardisierung der Spaltennamen.
* Konvertierung des Datumsformats.
* Identifikation ungültiger Datensätze.
* Entfernung ungültiger Datensätze.
* Entfernung von Duplikaten.

## Schritt 5 — Feature Engineering

Es werden mehrere zusätzliche Merkmale (Features) erstellt.

### Daily Return

```text
(close_price - previous_close) / previous_close
```

### Moving Average

Gleitende Durchschnitte:

```text
7 Tage

30 Tage
```

### Volatility

Die Volatilität wird für folgende Zeiträume berechnet:

```text
7 Tage

30 Tage
```

### Volume Change

Veränderung des Handelsvolumens zwischen zwei aufeinanderfolgenden Tagen.

### Time Features

Zeitbezogene Merkmale:

```text
year

month

day_of_week
```

## Schritt 6 — ML Preparation

Es wird ein spezifischer Datensatz für das Machine Learning erstellt.

Die Zielvariable ist:

```text
target_direction
```

Mögliche Werte:

```text
1 = Der Preis am folgenden Tag steigt.

0 = Der Preis am folgenden Tag fällt oder bleibt unverändert.
```

## Schritt 7 — Temporal Split

Die Daten werden nach einem zeitbasierten Ansatz aufgeteilt:

```text
TRAIN

Vor 2020


VALIDATION

2020 – 2022


TEST

2023+
```

## Schritt 8 — Storage

Die verarbeiteten Datensätze werden im Parquet-Format in MinIO gespeichert.

```text
processed/clean/

processed/features/

ml/train/

ml/validation/

ml/test/
```

## Schritt 9 — Serving Layer

Die für die Bereitstellung benötigten Daten werden in PostgreSQL geladen.

Anschließend können die Daten über SQL abgefragt oder über FastAPI als REST-API bereitgestellt werden.
