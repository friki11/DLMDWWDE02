# Technische Architektur

## Überblick

Dieses Projekt implementiert ein System zur Verarbeitung, Transformation, Speicherung und Bereitstellung historischer Daten des S&P-500-Aktienmarktes.

## Komponenten

### Ingestion Service

Der Ingestion Service ist für das Laden des Quelldatensatzes in den MinIO Data Lake verantwortlich.

Verantwortlichkeiten:

* Einlesen des CSV-Datensatzes.
* Überprüfung der Verfügbarkeit der Datei.
* Verbindung zu MinIO.
* Erstellung oder Verwendung des Data-Lake-Buckets.
* Hochladen der Daten in die RAW-Zone.

### MinIO Data Lake

MinIO wird als Objektspeicher verwendet, der mit der Amazon-S3-API kompatibel ist.

Der Data Lake ist in mehrere Zonen unterteilt:

```text
RAW
│
└── Originaldaten

PROCESSED
│
├── clean
│
└── features

ML
│
├── train
├── validation
└── test
```

### Processing Service

Der Processing Service verwendet Apache Spark zur Verarbeitung des Datensatzes.

Die wesentlichen Verarbeitungsschritte sind:

* Data Quality Checks.
* Data Cleaning.
* Feature Engineering.
* Vorbereitung der Daten für Machine Learning.

### PostgreSQL

PostgreSQL bildet die Serving Layer.

Es ermöglicht:

* Die strukturierte Speicherung der Daten.
* Die Optimierung von Abfragen.
* Die Erstellung von Views.
* Die Bereitstellung der Daten für Anwendungen.

### FastAPI

FastAPI stellt eine REST-API zur Verfügung, über die auf die Projektdaten zugegriffen werden kann.

Beispiele für Endpoints:

```text
GET /health

GET /tickers

GET /tickers/{ticker}

GET /tickers/{ticker}/history
```

## Containerisierung

Alle Komponenten werden mit Docker Compose orchestriert.

Die wichtigsten Services sind:

```text
MinIO
MinIO Init
Ingestion Service
Processing Service
Loading Service
PostgreSQL
API
```

## Docker-Netzwerk

Alle Services kommunizieren über ein dediziertes Docker-Netzwerk:

```text
sp500-network
```

Die Services verwenden ihre Docker-Namen als interne Hostnamen.

Beispiele:

```text
http://minio:9000

postgres:5432
```