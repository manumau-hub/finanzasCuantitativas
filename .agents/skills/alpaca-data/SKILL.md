---
name: alpaca-data
description: "Market Data API de Alpaca: acciones, crypto, opciones. Historical y real-time data para 5000+ stocks."
license: MIT
---

# Alpaca Data — Market Data API

API de datos de mercado con datos históricos y en tiempo real para acciones, crypto y opciones.

**Base URL:** `https://data.alpaca.markets`  
**SDK:** `pip install alpaca-py`  
**Docs:** [docs.alpaca.markets](https://docs.alpaca.markets/us/docs/about-market-data-api)

---

## Autenticación

### Obtener API Keys

1. Ir a [app.alpaca.markets](https://app.alpaca.markets)
2. Crear cuenta (paper trading es gratis)
3. Ir a "API Keys" → Generate New Keys
4. Guardar **API Key** y **Secret Key**

### Configuración

```python
import os
from alpaca.data.historical import StockHistoricalDataClient

# Keys (requerido para datos de acciones)
API_KEY = os.getenv("APCA_API_KEY_ID")
SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")

client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# Crypto NO requiere keys
from alpaca.data.historical import CryptoHistoricalDataClient
crypto_client = CryptoHistoricalDataClient()
```

**⚠️ NUNCA hardcodear keys en código que se comparte.**

---

## Rate Limits

| Plan | Requests/Min | Datos |
|------|-------------|-------|
| **Free (IEX)** | 200 | ~5 años historia, 1 exchange |
| **Paid (SIP)** | Mayor | Todas las bolsas US, ~7 años |

### Recomendaciones

- **Cachear datos** — los datos históricos no cambian
- **Batch requests** — pedir múltiples símbolos en una llamada
- **Usar `limit=10000`** — máximo por request
- **Paginar con `next_page_token`** — para datos grandes

---

## Data Feeds

| Feed | Descripción | Costo |
|------|-------------|-------|
| `iex` | Investors Exchange (~2.5% del volumen) | Gratis |
| `sip` | Todas las bolsas US (consolidado) | Paid |
| `boats` | Blue Ocean ATS (horas extendidas) | Paid |
| `otc` | Over-the-counter | Paid |

**Free tier = solo IEX**

---

## Historical Stock Data

### Bars (OHLCV)

```python
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

request = StockBarsRequest(
    symbol_or_symbols=["AAPL", "GOOGL"],
    timeframe=TimeFrame.Day,
    start=datetime(2023, 1, 1),
    end=datetime(2024, 12, 31),
    feed="iex"  # free tier
)

bars = client.get_stock_bars(request)
df = bars.df  # DataFrame
```

**TimeFrames disponibles:**
- `TimeFrame.Minute` / `TimeFrame(5, TimeFrame.Minute)`
- `TimeFrame.Hour`
- `TimeFrame.Day`
- `TimeFrame.Week`
- `TimeFrame.Month`

### Quotes (Bid/Ask)

```python
from alpaca.data.requests import StockQuotesRequest

request = StockQuotesRequest(
    symbol_or_symbols=["AAPL"],
    start=datetime(2024, 1, 1),
    end=datetime(2024, 1, 31),
    feed="iex"
)

quotes = client.get_stock_quotes(request)
```

### Trades

```python
from alpaca.data.requests import StockTradesRequest

request = StockTradesRequest(
    symbol_or_symbols=["AAPL"],
    start=datetime(2024, 1, 1),
    feed="iex"
)

trades = client.get_stock_trades(request)
```

### Latest Data

```python
# Latest bar
bars = client.get_stock_latest_bar(["AAPL", "GOOGL"])

# Latest quote
quotes = client.get_stock_latest_quote(["AAPL"])

# Latest trade
trades = client.get_stock_latest_trade(["AAPL"])
```

### Snapshots

```python
from alpaca.data.requests import SnapshotRequest

request = SnapshotRequest(
    symbol_or_symbols=["AAPL", "GOOGL"]
)
snapshots = client.get_snapshot(request)
```

---

## Historical Crypto Data

**No requiere API keys**

```python
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

client = CryptoHistoricalDataClient()

request = CryptoBarsRequest(
    symbol_or_symbols=["BTC/USD", "ETH/USD"],
    timeframe=TimeFrame.Day,
    start=datetime(2023, 1, 1),
    end=datetime(2024, 12, 31)
)

bars = client.get_crypto_bars(request)
df = bars.df
```

### Crypto Orderbook

```python
from alpaca.data.requests import CryptoLatestQuoteRequest

request = CryptoLatestQuoteRequest(symbol_or_symbols=["BTC/USD"])
quotes = client.get_crypto_latest_quote(request)
```

---

## Historical Options Data

### Option Chains

```python
# Obtener contratos disponibles
from alpaca.data.requests import OptionContractsRequest

request = OptionContractsRequest(
    underlying_symbols=["AAPL"],
    expiration_date_gte="2024-01-01",  # desde esta fecha
    expiration_date_lte="2024-12-31",  # hasta esta fecha
    strike_price_gte=100,  # strikes mínimo
    strike_price_lte=200   # strikes máximo
)

contracts = client.get_option_contracts(request)
```

### Option Bars/Trades/Quotes

```python
from alpaca.data.requests import OptionBarsRequest

# Buscar contract ID primero
contract_id = "6e58f870-fe73-4583-81e4-b9a37892c36f"

request = OptionBarsRequest(
    symbol_or_contract_ids=[contract_id],
    start=datetime(2024, 1, 1),
    end=datetime(2024, 1, 31)
)

bars = client.get_option_bars(request)
```

---

## Options Tickers Reference

Ver [./references/options_reference.md](./references/options_reference.md) para:
- Símbolos de opciones (AAPL240119C00100000)
- Parámetros de filtrado
- Trading levels requeridos

---

## News

```python
from alpaca.data.requests import StockNewsRequest

request = StockNewsRequest(
    symbol_or_symbols=["AAPL", "GOOGL"],
    start=datetime(2024, 1, 1),
    end=datetime(2024, 1, 31)
)

news = client.get_stock_news(request)
```

---

## Screener

```python
from alpaca.data.requests import MostActivesRequest

request = MostActivesRequest(
    by="volume",  # volume, share, number
    top=10,
    date="2024-01-15"
)

movers = client.get_most_actives(request)
```

---

## WebSocket Real-Time (Opcional)

```python
from alpaca.data.stream import StockDataStream

ws = StockDataStream(API_KEY, SECRET_KEY)

async def handle_bar(bar):
    print(bar)

ws.subscribe_bars(handle_bar, "AAPL", "GOOGL")
ws.run()
```

---

## Scripts de Descarga

Usá los scripts en [./scripts/](./scripts/):

```bash
# Descargar bars de acciones
python ./scripts/download_stock_bars.py --symbols AAPL,GOOGL --days 365 --output data/

# Descargar crypto
python ./scripts/download_crypto_bars.py --symbols BTC,ETH --days 90 --output data/

# Descargar option contracts
python ./scripts/download_options.py --symbol AAPL --output data/
```

---

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 403 Forbidden | Keys inválidas o sin permisos | Verificar API keys |
| 429 Too Many Requests | Rate limit | Esperar, usar cache |
| Empty response | Sin datos para el símbolo | Verificar símbolo |
| "options_enabled" | Symbol sin opciones | Usar símbolo con opciones |

---

## Comparación con Otras APIs

| Feature | Alpaca | Alpha Vantage | Data912 |
|---------|--------|---------------|---------|
| Free tier | ✅ IEX (1 exchange) | ✅ 25/day | ✅ Todo ARS |
| Stocks US | ✅ | ✅ | ❌ |
| Crypto | ✅ | ✅ | ❌ |
| Opciones | ✅ | ❌ | ❌ |
| Historical depth | ~5 años IEX | Limitado | Limitado |
| SDK Python | ✅ alpaca-py | ✅ | ❌ |

**Elegí Alpaca para:** datos de EE.UU. (stocks, crypto, opciones), datos intraday.  
**Elegí Data912 para:** datos del mercado argentino.  
**Elegí Alpha Vantage para:** indicadores técnicos, forex.
