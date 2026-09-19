---
name: alpha-vantage
description: "API de datos financieros de EE.UU.: acciones, forex, crypto, indicadores técnicos, fundamental data."
license: MIT
---

# Alpha Vantage — Financial Data API

**⚠️ IMPORTANTE: Requiere API Key gratuita. Ver sección de Autenticación.**

API de datos financieros con cobertura global (20+ bolsas, 200,000+ tickers).

**Base URL:** `https://www.alphavantage.co/query`  
**Documentación completa:** [alphavantage.co/documentation](https://www.alphavantage.co/documentation/)

---

## Autenticación

### Obtener API Key (GRATIS)

1. Ir a: https://www.alphavantage.co/support/#api-key
2. Completar el formulario (email, nombre, tipo de uso)
3. Recibir key instantáneamente por email
4. **No requiere tarjeta de crédito**

### Usar la API Key

```python
import os
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")  # Recomendado
# o directamente:
API_KEY = "TU_API_KEY_AQUI"
```

**⚠️ NUNCA hardcodear la API key en código que se va a compartir/commits.**

---

## Rate Limits

| Plan | Requests/Día | Requests/Minuto | Precio |
|------|--------------|-----------------|--------|
| **Free** | 25 | 5 | $0 |
| Standard | ∞ | 75 | $49.99/mes |
| Premium | ∞ | 150 | $99.99/mes |
| Enterprise | ∞ | 1,200 | $249.99/mes |

### Recomendaciones para Free Tier

- **Cachear respuestas** — los datos no cambian frecuentemente
- **Usar `outputsize=compact`** — retorna últimos 100 datos (gratis)
- **No hacer llamadas en cada request de usuario**
- **Esperar 12+ segundos entre requests** (5 req/min máximo)

### Si llegás al límite

El API retorna:
```json
{
  "Error Message": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 requests per minute and 25 requests per day. Please subscribe to a premium plan for higher API call volume."
}
```

---

## Endpoints Disponibles

### Time Series — Acciones (Free Tier)

| Function | Descripción | Notas |
|----------|-------------|-------|
| `TIME_SERIES_DAILY` | OHLCV diario | ⚠️ Solo `compact` (100 datos) |
| `TIME_SERIES_WEEKLY` | OHLCV semanal | Full history |
| `TIME_SERIES_MONTHLY` | OHLCV mensual | Full history |
| `GLOBAL_QUOTE` | Quote último precio | Rápido |
| `SYMBOL_SEARCH` | Buscar símbolos | |

### Time Series — PREMIUM

| Function | Descripción |
|----------|-------------|
| `TIME_SERIES_INTRADAY` | Datos intraday (1/5/15/30/60 min) |
| `TIME_SERIES_DAILY_ADJUSTED` | Con splits/dividendos |
| `outputsize=full` | Historia completa (20+ años) |

### Fundamental Data (Free Tier)

| Function | Descripción |
|----------|-------------|
| `OVERVIEW` | Company overview |
| `INCOME_STATEMENT` | Estado de resultados |
| `BALANCE_SHEET` | Balance general |
| `CASH_FLOW` | Flujo de caja |
| `EARNINGS` | Ganancias históricas |

### Forex (Free Tier)

| Function | Descripción |
|----------|-------------|
| `CURRENCY_EXCHANGE_RATE` | Tipo de cambio actual |
| `FX_INTRADAY` | Intraday forex |
| `FX_DAILY` | Forex diario |
| `FX_WEEKLY` | Forex semanal |
| `FX_MONTHLY` | Forex mensual |

### Cryptocurrency (Free Tier)

| Function | Descripción |
|----------|-------------|
| `CURRENCY_EXCHANGE_RATE` | Crypto vs fiat |
| `DIGITAL_CURRENCY_DAILY` | Crypto diario |
| `DIGITAL_CURRENCY_WEEKLY` | Crypto semanal |
| `DIGITAL_CURRENCY_MONTHLY` | Crypto mensual |

### Technical Indicators (50+ Free Tier)

Ver lista completa en [./references/indicators.md](./references/indicators.md):

| Categoría | Indicadores |
|-----------|-------------|
| **Trend** | SMA, EMA, WMA, DEMA, TEMA, KAMA, etc. |
| **Momentum** | RSI, MACD, STOCH, WILLR, ADX, CCI, etc. |
| **Volatility** | BBANDS, ATR, NATR, TRANGE |
| **Volume** | OBV, AD, ADOSC |

### Economic Indicators (Free Tier)

| Function | Descripción |
|----------|-------------|
| `REAL_GDP` | PIB de EE.UU. |
| `CPI` | Índice de Precios al Consumidor |
| `INFLATION` | Tasa de inflación |
| `UNEMPLOYMENT` | Tasa de desempleo |
| `FEDERAL_FUNDS_RATE` | Tasa de fondos federales |
| `TREASURY_YIELD` | Rendimientos del tesoro |

### Alpha Intelligence (Free Tier)

| Function | Descripción | Notas |
|----------|-------------|-------|
| `NEWS_SENTIMENT` | Análisis de sentimiento | Free |
| `TOP_GAINERS_LOSERS` | Mejores/peores | Free |
| `INSIDER_TRANSACTIONS` | Transacciones insiders | ⚠️ PREMIUM |
| `ANALYTICS_FIXED_WINDOW` | Analytics avanzado | ⚠️ PREMIUM |

---

## Ejemplos de Uso

### Quote actual (más simple)

```python
import requests

url = "https://www.alphavantage.co/query"
params = {
    "function": "GLOBAL_QUOTE",
    "symbol": "AAPL",
    "apikey": API_KEY
}
r = requests.get(url, params=params)
quote = r.json()["Global Quote"]
print(f"AAPL: ${quote['05. price']}")
```

### Time Series Diario

```python
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "IBM",
    "outputsize": "compact",  # últimos 100 días (free)
    "apikey": API_KEY
}
r = requests.get(url, params=params)
data = r.json()["Time Series (Daily)"]
```

### Indicador Técnico (RSI)

```python
params = {
    "function": "RSI",
    "symbol": "IBM",
    "interval": "daily",
    "time_period": 14,
    "apikey": API_KEY
}
```

### Forex

```python
params = {
    "function": "CURRENCY_EXCHANGE_RATE",
    "from_currency": "BTC",
    "to_currency": "USD",
    "apikey": API_KEY
}
```

---

## Scripts de Descarga

Usá los scripts en [./scripts/](./scripts/):

```bash
# Descargar quotes de múltiples símbolos
python ./scripts/download_quotes.py --symbols AAPL,GOOGL,MSFT --output data/

# Descargar time series diarios
python ./scripts/download_timeseries.py --symbol AAPL --output data/

# Descargar indicadores técnicos
python ./scripts/download_indicators.py --symbol AAPL --indicator RSI --output data/
```

---

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "5 requests per minute" | Rate limit | Esperar 12+ segundos |
| "25 requests per day" | Daily limit | Esperar 24 horas o upgrade |
| "Invalid API call" | Symbol no existe | Usar `SYMBOL_SEARCH` primero |
| "premium" en response | Endpoint premium | Usar alternativa free o upgrade |
