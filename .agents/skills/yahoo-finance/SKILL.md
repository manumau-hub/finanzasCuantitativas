---
name: yahoo-finance
description: "API no oficial de Yahoo Finance: precios, históricos, fundamentales, opciones, noticias en JSON puro sin wrappers."
license: MIT
---

# Yahoo Finance — API Directa (sin yfinance)

API no oficial de Yahoo Finance. Accedé a datos de **acciones, ETFs, crypto, forex, bonos, índices, opciones, fundamentos y noticias** mediante **requests HTTP directos** sin usar `yfinance` ni ningún wrapper.

**Base URL:** `https://query1.finance.yahoo.com`
**Alternativa:** `https://query2.finance.yahoo.com`

---

## ⚠️ Importante

- Yahoo **no tiene API pública oficial** desde 2017. Estos endpoints son no oficiales y pueden cambiar sin aviso.
- Algunos endpoints requieren autenticación via **cookie + crumb** (abajo se explica).
- El endpoint `v8/finance/chart` funciona sin autenticación (solo User-Agent de navegador).
- Siempre implementar **rate limiting** y **manejo de errores**.

---

## Documentación completa

Para referencia exhaustiva de todos los endpoints, campos, JSON structures, códigos de error, tickers internacionales, estrategias de rate limiting y ejemplos detallados, ver:

📖 **[references/API_REFERENCE.md](./references/API_REFERENCE.md)**

Ese documento incluye:
- Los **33 módulos** de `quoteSummary` con cada campo documentado
- JSON responses **completas** de cada endpoint
- **Tickers internacionales** (`.BA` para Argentina, `.SA` para Brasil, etc.)
- **WebSocket streaming**
- **Screener**, **lookup**, **trending**
- **Estrategias de rate limiting** con exponential backoff y rotación de User-Agent

---

## Autenticación: Cookie + Crumb

Varios endpoints requieren un **crumb** (token CSRF) que se obtiene con cookies de sesión.

```python
import requests

BASE = "https://query1.finance.yahoo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def yahoo_session():
    """Retorna requests.Session con cookie A3 y crumb."""
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get("https://fc.yahoo.com", timeout=10)
    crumb = s.get(f"{BASE}/v1/test/getcrumb", timeout=10).text.strip()
    s.params = {"crumb": crumb}
    return s

# Uso:
# s = yahoo_session()
# r = s.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL,MSFT")
```

### Endpoints según autenticación

| Sin auth (solo User-Agent) | Requieren crumb |
|----------------------------|-----------------|
| `v8/finance/chart` (históricos) | `v7/finance/quote` (precios) |
| `v1/finance/search` (búsqueda) | `v10/finance/quoteSummary` (fundamentos) |
| `v1/finance/trending` (tendencias) | `v7/finance/options` (opciones) |
| `v1/finance/lookup` (lookup) | `v6/finance/recommendationsbysymbol` |

---

## Endpoints — Resumen rápido

### 1. Históricos OHLCV — `v8/finance/chart`

GET https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1y&interval=1d

| Parámetro | Ejemplos |
|-----------|----------|
| `range` | `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `5y`, `10y`, `ytd`, `max` |
| `interval` | `1m`, `5m`, `15m`, `1h`, `1d`, `1wk`, `1mo` |
| `events` | `div,splits` (incluye dividendos y splits) |

```python
import requests
headers = {"User-Agent": "Mozilla/5.0 (...) Chrome/120.0.0.0 Safari/537.36"}
r = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AAPL",
                 params={"range": "1y", "interval": "1d", "events": "div,splits"},
                 headers=headers)
data = r.json()["chart"]["result"][0]
# data["timestamp"] -> fechas Unix
# data["indicators"]["quote"][0] -> open, high, low, close, volume
# data["indicators"]["adjclose"][0] -> precios ajustados
# data["events"] -> dividendos y splits
```

### 2. Quote — `v7/finance/quote`

```python
s = yahoo_session()
r = s.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL,MSFT,GOOGL")
quotes = r.json()["quoteResponse"]["result"]
for q in quotes:
    print(q["symbol"], q["regularMarketPrice"], q["regularMarketChangePercent"])
```

Campos: `regularMarketPrice`, `regularMarketChangePercent`, `marketCap`, `trailingPE`, `fiftyTwoWeekHigh/Low`, `dividendYield`, `volume`, `marketState` (PRE/REGULAR/POST/CLOSED).

### 3. Fundamentos — `v10/finance/quoteSummary`

```python
s = yahoo_session()
r = s.get("https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL",
          params={"modules": "assetProfile,financialData,defaultKeyStatistics,incomeStatementHistory,balanceSheetHistory,cashflowStatementHistory,earnings,recommendationTrend"})
fundamentals = r.json()["quoteSummary"]["result"][0]
profile = fundamentals["assetProfile"]           # sector, industry, employees, description
financials = fundamentals["financialData"]        # EBITDA, revenue, margins, ROE, ROA
stats = fundamentals["defaultKeyStatistics"]      # beta, shares, PE, PEG, short info
```

Hay **33 módulos disponibles**. Ver lista completa en [API_REFERENCE.md sección 4](./references/API_REFERENCE.md#4-v10financequotesummary--fundamentos).

### 4. Opciones — `v7/finance/options`

```python
s = yahoo_session()
r = s.get("https://query1.finance.yahoo.com/v7/finance/options/AAPL")
data = r.json()["optionChain"]["result"][0]
expirations = data["expirationDates"]
strikes = data["strikes"]
options = data["options"][0]  # calls + puts
```

### 5. Búsqueda + Noticias — `v1/finance/search`

```python
r = requests.get("https://query1.finance.yahoo.com/v1/finance/search",
                 params={"q": "Apple", "quotesCount": 3, "newsCount": 5},
                 headers=HEADERS)
data = r.json()
# data["quotes"] -> tickers encontrados
# data["news"] -> noticias relacionadas
```

---

## Scripts

| Script | Descripción |
|--------|-------------|
| **[batch_fetch.py](./scripts/batch_fetch.py)** | Batch multi-ticker con token bucket + ThreadPoolExecutor. Quote batching (todos en 1 request). Charts en paralelo respetando rate limit. |
| **[fetch_all.py](./scripts/fetch_all.py)** | Script integral: fetch de histórico + quote + fundamentals + opciones + search + recomendaciones. Genérico para cualquier ticker con argumentos CLI. |
| **[fetch_quote.py](./scripts/fetch_quote.py)** | Fetch rápido de quote + fundamentals por ticker. |
| **[download_historical.py](./scripts/download_historical.py)** | Descarga históricos OHLCV a CSV. |

### batch_fetch.py — Batch multi-ticker con rate limiting

```
# Test seguro (3 tickers, solo chart, 2 req/s)
py scripts/batch_fetch.py --tickers AAPL,MSFT,NVDA --chart --rate 2.0

# Batch completo (quote en 1 request + charts en paralelo)
py scripts/batch_fetch.py --tickers AAPL,MSFT,NVDA,GOOGL,META,AMZN,TSLA --all --rate 2.0 --workers 4

# Solo quotes (siempre 1 request, imposible rate-limit)
py scripts/batch_fetch.py --tickers AAPL,MSFT,NVDA,GOOGL --quote

# Personalizar rate + workers
py scripts/batch_fetch.py --tickers AAPL,MSFT,NVDA --all --rate 1.5 --workers 3 --range 5y
```

**Flags clave:**
- `--rate` : tokens/segundo del token bucket (default: 2.0 — máximo seguro)
- `--burst` : tokens acumulables para ráfagas (default: 5)
- `--workers` : hilos en paralelo (default: 4)

**Arquitectura:**
1. **Fase 1 — Quote batch**: todos los tickers en 1 sola request (`v7/finance/quote?symbols=AAPL,MSFT,...`)
2. **Fase 2 — Token bucket**: `ThreadPoolExecutor` con `TokenBucket` thread-safe compartido entre workers. Cada worker adquiere un token antes de cada request. A 2 req/s con burst=5, se pueden lanzar hasta 5 requests instantáneas sin bloquear; luego el bucket estabiliza el throughput.

### fetch_all.py — El script principal

```
python scripts/fetch_all.py --ticker AAPL --all                     # Todo lo disponible
python scripts/fetch_all.py --ticker GGAL --all --range 5y --interval 1d  # GGAL con 5 años
python scripts/fetch_all.py --ticker MSFT --chart --range max        # Histórico completo
python scripts/fetch_all.py --ticker NVDA --quote --fundamentals     # Quote + fundamentals
python scripts/fetch_all.py --ticker TSLA --all --all-modules        # Todos los módulos (~33)
python scripts/fetch_all.py --ticker AAPL --options                  # Solo opciones
python scripts/fetch_all.py -t AAPL -o mi_data.json -q               # Output a archivo, quiet
```

**Flags principales:**
- `--all` : fetch de todo (chart, quote, fundamentals, options, search, recommendations)
- `--chart` : histórico OHLCV
- `--quote` : precio en tiempo real
- `--fundamentals` : fundamentos (quoteSummary)
- `--options` : cadena de opciones
- `--search` : búsqueda y noticias
- `--range` / `--interval` : control del histórico
- `--modules` / `--all-modules` : módulos de quoteSummary
- `--output` : archivo JSON de salida

### Prueba real con GGAL (testeado)

```
>> Chart (1y, 1d)... OK 250 bars
>> Quote...             OK Price: $50.33 (-1.62%)
>> Fundamentals...      OK 12 módulos (core)
>> Options...           OK 5 expiration dates, 17 calls, 19 puts
>> Search+News...       OK 5 news items
Guardado en: ggal_temp.json  (123 KB)
```

---

## Tickers internacionales

Yahoo Finance usa sufijos para mercados fuera de EE.UU.:

| Mercado | Sufijo | Ejemplo |
|---------|--------|---------|
| Argentina (BCBA) | `.BA` | `GGAL.BA`, `YPFD.BA` |
| Brasil (Bovespa) | `.SA` | `PETR4.SA`, `VALE3.SA` |
| México (BMV) | `.MX` | `WALMEX.MX` |
| Crypto | `-USD` | `BTC-USD`, `ETH-USD` |
| Forex | `=X` | `EURUSD=X` |
| Índices | `^` | `^GSPC` (S&P 500) |

Ver lista completa en [API_REFERENCE.md sección 14](./references/API_REFERENCE.md#14-tickers-internacionales).

---

## Rate Limits

| Límite | Comportamiento |
|--------|----------------|
| ~2 req/s | Seguro |
| 3-5 req/s | Probabilidad alta de 429 |
| >10 req/s | IP block temporal |

**Siempre usar `time.sleep(0.5)` entre requests e implementar exponential backoff.**

Para fetch multi-ticker, usar [`batch_fetch.py`](./scripts/batch_fetch.py) que implementa token bucket a 2 req/s con burst de 5. A diferencia de yfinance (que no tiene rate limiter y lanza N threads simultáneos), batch_fetch garantiza que el throughput agregado no supere el límite seguro.

---

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `401 Unauthorized` | Falta crumb | Usar `yahoo_session()` |
| `429 Too Many Requests` | Rate limit | Esperar 30-60s |
| `Bad Request` | Crumb expirado | Regenerar crumb |
| `result` vacío | Ticker inválido | Verificar con search primero |
| `Python-requests` block | User-Agent default | Setear uno de navegador |

---

## Estructura del skill

```
skills/yahoo-finance/
├── SKILL.md                          # Este archivo (quickstart)
├── references/
│   └── API_REFERENCE.md              # Documentación completa de todos los endpoints
└── scripts/
    ├── batch_fetch.py                # Batch multi-ticker con rate limiting (recomendado)
    ├── fetch_all.py                  # Script integral
    ├── fetch_quote.py                # Quote + fundamentals rápido
    └── download_historical.py        # Históricos a CSV
```
