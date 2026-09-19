---
name: data912
description: "API del mercado argentino: acciones, CEDEARs, bonos, MEP, CCL con datos live e históricos (OHLC)."
license: MIT
---

# Data912 — data912.com API

API gratuita con datos del mercado argentino. Refresca cada 20 segundos, rate limit 120 req/min.

**Base URL:** `https://data912.com`

## Endpoints Live

Consultar precios en tiempo real:

| Endpoint | Descripción |
|----------|-------------|
| `/live/mep` | USD MEP implícito |
| `/live/ccl` | USD CCL implícito |
| `/live/arg_stocks` | Acciones argentinas |
| `/live/arg_options` | Opciones |
| `/live/arg_cedears` | CEDEARs |
| `/live/arg_notes` | Notas gubernamentales |
| `/live/arg_corp` | Deuda corporativa |
| `/live/arg_bonds` | Bonos gubernamentales |
| `/live/usa_adrs` | ADRs estadounidenses |
| `/live/usa_stocks` | Acciones estadounidenses |

### Ejemplo live

```python
import requests
r = requests.get("https://data912.com/live/arg_stocks")
df = pd.DataFrame(r.json())
```

## Endpoints Históricos (OHLC)

Descargá el catálogo de tickers en [./references/tickers_stocks.md](./references/tickers_stocks.md), [./references/tickers_cedears.md](./references/tickers_cedears.md) y [./references/tickers_bonds.md](./references/tickers_bonds.md).

| Endpoint | Descripción |
|----------|-------------|
| `/historical/stocks/{ticker}` | OHLC de acciones argentinas |
| `/historical/cedears/{ticker}` | OHLC de CEDEARs |
| `/historical/bonds/{ticker}` | OHLC de bonos |

### Ejemplo histórico

```python
ticker = "GGAL"
r = requests.get(f"https://data912.com/historical/stocks/{ticker}")
df = pd.DataFrame(r.json())
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()
```

**Campos OHLC:** `date`, `o` (open), `h` (high), `l` (low), `c` (close), `v` (volume), `dr` (daily return), `sa` (sigma annualized)

## Volatilidades (EOD)

```python
ticker = "YPF"
r = requests.get(f"https://data912.com/eod/volatilities/{ticker}")
```

**Campos:** IV short/medium/long term, HV short/medium/long term, IV/HV ratios y percentiles, fair IV.

## Descargar CSV de históricos

Usá el script [./scripts/download_historical.py](./scripts/download_historical.py):

```bash
python ./scripts/download_historical.py --type stocks --tickers GGAL,PAMP,YPFD --output data/
python ./scripts/download_historical.py --type cedears --tickers AAPL,GOOGL,MSFT --output data/
python ./scripts/download_historical.py --type bonds --tickers AL30,GD30,GD35 --output data/
python ./scripts/download_historical.py --type all --tickers GGAL,AL30,AAPL --output data/
```

## Rate Limits

- **120 requests/minuto** por endpoint
- Datos refresh cada 20 segundos (no es real-time real)
- Sin autenticación requerida
