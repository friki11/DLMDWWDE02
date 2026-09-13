# REST-API

## Ziel

Die REST-API ermöglicht den Zugriff auf die in PostgreSQL gespeicherten Finanzmarktdaten.

## Basis-URL

```text
http://localhost:8000
```

## Health Check

### Anfrage

```text
GET /health
```

### Antwort

```json
{
    "status": "healthy",
    "service": "sp500-api"
}
```

## Ticker abrufen

### Anfrage

```text
GET /tickers
```

### Beschreibung

Gibt eine Liste der verfügbaren Ticker zurück.

## Ticker abrufen

### Anfrage

```text
GET /tickers/{ticker}
```

### Beispiel

```text
GET /tickers/AAPL
```

Gibt die zuletzt verfügbaren Informationen für einen bestimmten Ticker zurück.

## Historische Daten eines Tickers abrufen

### Anfrage

```text
GET /tickers/{ticker}/history
```

### Beispiel

```text
GET /tickers/AAPL/history
```

### Parameter

```text
limit
```

Beispiel:

```text
GET /tickers/AAPL/history?limit=100
```

## Swagger-Dokumentation

FastAPI stellt automatisch eine interaktive API-Dokumentation zur Verfügung.

```text
http://localhost:8000/docs
```
