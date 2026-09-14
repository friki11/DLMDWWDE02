# Data Quality

## NULL-Werte

Jede Spalte wird analysiert, um fehlende Werte zu identifizieren.

NULL-Werte sind insbesondere bei den folgenden Finanzspalten relevant:

```text
Open

High

Low

Close

Volume
```

## Doppelte Datensätze

Es werden zwei verschiedene Prüfungen durchgeführt.

### Doppelte Zeilen

Erkennung von Zeilen, die vollständig identisch sind.

### Doppelte Kombination aus Datum und Ticker

Erkennung doppelter Kombinationen aus:

```text
Date + Ticker
```

Jeder Ticker sollte normalerweise nur eine Beobachtung pro Datum enthalten.

## Negative Werte

Negative Werte werden für folgende Spalten überprüft:

```text
Adj Close

Close

Dividends

High

Low

Open

Volume

Stock Splits
```

Negative Preis- und Volumenwerte werden als potenziell ungültig betrachtet.

## Konsistenz

Die Daten müssen grundsätzlich die folgenden Bedingungen erfüllen:

```text
High >= Low

High >= Open

High >= Close

Low <= Open

Low <= Close
```

Datensätze, die diese Bedingungen nicht erfüllen, werden als potenziell fehlerhaft gekennzeichnet.

## Ergebnisse

Ungültige Datensätze werden anschließend im Rahmen des Data-Cleaning-Schritts entfernt.
