# Markets, Exchanges y Countries — Referencia

> Lista de mercados, exchanges y paises usables como `market`,
> `exchange` filter y `country` filter en el Scanner API y Symbol Search.

---

## Indice

1. [Markets validos](#1-markets-validos)
2. [Exchanges por mercado](#2-exchanges-por-mercado)
3. [Countries validos](#3-countries-validos)
4. [Tickers — formato por mercado](#4-tickers--formato-por-mercado)
5. [Decisiones tipicas: que market usar](#5-decisiones-tipicas-que-market-usar)
6. [Lista completa de exchanges identificados](#6-lista-completa-de-exchanges-identificados)

---

## 1. Markets validos

El parametro `{market}` en `POST /{market}/scan` controla el universo que
se consulta. Lista verificada al 2026-06.

| Market | Descripcion | Cobertura aprox |
|--------|-------------|-----------------|
| `global` | Universo combinado | 100k+ |
| `america` | NYSE + NASDAQ + AMEX + OTC | 15k+ |
| `argentina` | BCBA / BYMA | 300+ |
| `brazil` | B3 / Bovespa | 500+ |
| `spain` | BME | 200+ |
| `italy` | Borsa Italiana | 400+ |
| `germany` | Xetra + Frankfurt | 1000+ |
| `uk` | LSE | 2000+ |
| `france` | Euronext Paris | 800+ |
| `russia` | MOEX | 200+ |
| `crypto` | Cryptos | 50k+ |
| `forex` | Forex pairs | 1000+ |
| `bonds` | Bonos globales (TVC) | 300+ |

### Invalidos confirmados (HTTP 404)

`asia`, `world` — no existen como market segments.

---

## 2. Exchanges por mercado

### america

| Exchange code | Nombre | Tipos comunes |
|---------------|--------|---------------|
| `NASDAQ` | Nasdaq Stock Market | stocks, ETFs, dr (CEDEARs, ADRs) |
| `NYSE` | New York Stock Exchange | stocks, dr |
| `AMEX` | American Stock Exchange | ETFs principalmente |
| `OTC` | Over-the-counter | Stocks pequeñas, pink sheets |

### argentina (BYMA / BCBA)

| Exchange code | Nombre |
|---------------|--------|
| `BCBA` | Bolsa de Comercio de Buenos Aires (alias BYMA) |
| `BYMA` | Bolsas y Mercados Argentinos |

Ambos codes existen; `BCBA` es el mas usado historicamente.

### brazil

| Exchange code | Nombre |
|---------------|--------|
| `BMFBOVESPA` | B3 — Brasil Bolsa Balcao |

### spain

| Exchange code | Nombre |
|---------------|--------|
| `BME` | Bolsas y Mercados Españoles |

### italy

| Exchange code | Nombre |
|---------------|--------|
| `MIL` | Borsa Italiana (Milano) |
| `EUROTLX` | EuroTLX |

### germany

| Exchange code | Nombre |
|---------------|--------|
| `XETR` | Xetra |
| `FWB` | Frankfurter Wertpapierborse |
| `MUN`, `BER`, `DUS`, `HAM`, `STU` | Bolsas regionales |

### uk

| Exchange code | Nombre |
|---------------|--------|
| `LSE` | London Stock Exchange |
| `LSIN` | LSE International |
| `AQUIS` | Aquis Stock Exchange |

### france

| Exchange code | Nombre |
|---------------|--------|
| `EURONEXT` | Euronext (Paris, Amsterdam, Brussels) |

### crypto

| Exchange code | Nombre |
|---------------|--------|
| `BINANCE` | Binance |
| `COINBASE` | Coinbase |
| `BITSTAMP` | Bitstamp |
| `KRAKEN` | Kraken |
| `BYBIT` | Bybit |
| `OKX` | OKX |
| `BITFINEX` | Bitfinex |
| `HUOBI` | Huobi |
| `BITTREX` | Bittrex |
| `POLONIEX` | Poloniex |

### forex

| Exchange code | Nombre |
|---------------|--------|
| `FX` | FX (broker agregado) |
| `OANDA` | OANDA |
| `FX_IDC` | International Datacasting |
| `SAXO` | Saxo Bank |

### bonds

| Exchange code | Nombre |
|---------------|--------|
| `TVC` | TradingView (datos sinteticos de yield curves) |

---

## 3. Countries validos

Para filtrar por `country` en el Scanner:

```json
{"left": "country", "operation": "equal", "right": "Argentina"}
```

Lista de countries comunes (no exhaustiva — usar `equal` con cualquier
nombre estandar en ingles):

**Americas:**
`United States`, `Argentina`, `Brazil`, `Canada`, `Chile`, `Colombia`,
`Mexico`, `Peru`, `Uruguay`, `Venezuela`.

**Europa:**
`United Kingdom`, `Germany`, `France`, `Italy`, `Spain`, `Portugal`,
`Netherlands`, `Belgium`, `Switzerland`, `Austria`, `Sweden`, `Norway`,
`Denmark`, `Finland`, `Ireland`, `Poland`, `Czech Republic`, `Greece`,
`Russia`, `Turkey`, `Ukraine`.

**Asia:**
`Japan`, `China`, `Hong Kong`, `Taiwan`, `South Korea`, `India`,
`Singapore`, `Malaysia`, `Thailand`, `Indonesia`, `Philippines`, `Vietnam`,
`Israel`, `Saudi Arabia`, `United Arab Emirates`, `Qatar`.

**Oceania:**
`Australia`, `New Zealand`.

**Africa:**
`South Africa`, `Egypt`, `Nigeria`, `Kenya`, `Morocco`.

> **Importante:** la API es **case-sensitive** y exige el formato exacto
> en ingles. `argentina` (minuscula) → 0 results. `Argentina` → matches.

### Ejemplos:

```bash
# Empresas argentinas (incluye ADRs cotizando en US)
py fetch_tradingview.py country Argentina

# Empresas listadas EN argentina (local solo)
py fetch_tradingview.py screen --filter '[["country","equal","Argentina"],["exchange","equal","BCBA"]]'

# Empresas brasileras en NYSE (ADRs)
py fetch_tradingview.py screen --filter '[["country","equal","Brazil"],["exchange","equal","NYSE"]]'
```

---

## 4. Tickers — formato por mercado

| Mercado | Formato | Ejemplos |
|---------|---------|----------|
| US stocks | `{EXCHANGE}:{TICKER}` | `NASDAQ:AAPL`, `NYSE:JPM`, `AMEX:SPY` |
| US ADRs | `{EXCHANGE}:{TICKER}` | `NASDAQ:GGAL`, `NYSE:BBAR` (con D suffix para algunos) |
| Argentina | `BCBA:{TICKER}` | `BCBA:GGAL`, `BCBA:YPF`, `BCBA:PAMP` |
| Argentina CEDEARs | `BCBA:{TICKER}` (mismo formato local) | `BCBA:AAPL`, `BCBA:KO` |
| Brazil | `BMFBOVESPA:{TICKER}{NUM}` | `BMFBOVESPA:PETR4`, `BMFBOVESPA:VALE3` |
| Spain | `BME:{TICKER}` | `BME:SAN`, `BME:TEF`, `BME:IBE` |
| Germany | `XETR:{TICKER}` | `XETR:SAP`, `XETR:VOW3`, `XETR:BMW` |
| UK | `LSE:{TICKER}` | `LSE:HSBA`, `LSE:VOD` |
| Crypto | `{EXCHANGE}:{PAIR}` | `BINANCE:BTCUSDT`, `COINBASE:ETHUSD` |
| Forex | `FX:{PAIR}` | `FX:EURUSD`, `OANDA:GBPUSD` |
| Bonos | `TVC:{CODIGO}` | `TVC:US10Y`, `TVC:DE10Y`, `TVC:AR10Y` |
| Indices | `{EXCHANGE}:{INDEX}` | `INDEX:NDX`, `INDEX:DJI`, `INDEX:SPX`, `INDEX:ARG30` |

### URL HTML

Convertir `:` por `-`:

`NASDAQ:GGAL` → `https://es.tradingview.com/symbols/NASDAQ-GGAL/`

---

## 5. Decisiones tipicas: que market usar

### Buscar la GGAL en NASDAQ

→ `market=america` o `market=global` con ticker `NASDAQ:GGAL`.

```bash
py fetch_tradingview.py quote NASDAQ:GGAL --market global
```

### Buscar la GGAL local en BYMA

→ `market=argentina` con ticker `BCBA:GGAL`.

```bash
py fetch_tradingview.py quote BCBA:GGAL --market argentina
```

### Buscar TODAS las empresas argentinas en cualquier mercado

→ `market=global` + `filter` por country.

```bash
py fetch_tradingview.py country Argentina --market global --limit 30
```

### Buscar TOP cripto por market cap

→ `market=crypto`, sort por `market_cap_basic`.

```bash
py fetch_tradingview.py market crypto --limit 20
```

### Buscar AAPL en cualquier exchange del mundo

→ `symbol_search` (devuelve TODAS las variantes).

```bash
py fetch_tradingview.py search "AAPL" --type stocks
# Devuelve NASDAQ:AAPL + variantes en BMV, XETR, LSE, etc.
```

---

## 6. Lista completa de exchanges identificados

Esta lista fue compilada inspeccionando los `exchange` fields de los
responses del Scanner para diferentes paises. NO es exhaustiva (TradingView
soporta 100+ exchanges globales).

### Northamerica
NYSE, NASDAQ, AMEX, OTC, ARCA, BATS, IEX (US)
TSX, TSXV, CSE, NEO (Canada)
BMV (Mexico)

### Latinoamerica
BCBA / BYMA (Argentina)
BMFBOVESPA (Brazil)
BCS (Chile)
BVCA (Colombia)
BVL (Peru)

### Europa
LSE, LSIN, AQUIS (UK)
EURONEXT (France, Netherlands, Belgium)
XETR, FWB (Germany)
BME (Spain)
MIL, EUROTLX (Italy)
SIX (Switzerland)
WIENER, VIE (Austria)
WSE (Poland)
OMXSTO (Sweden)
OMXHEX (Finland)
OMXCOP (Denmark)

### Asia-Pacifico
TSE (Japan: Tokyo, alias JPX)
HKEX (Hong Kong)
SSE, SZSE (China: Shanghai, Shenzhen)
TWSE (Taiwan)
KRX (South Korea)
NSE, BSE (India)
ASX (Australia)
NZX (New Zealand)
SGX (Singapore)
SET (Thailand)
IDX (Indonesia)
KLSE (Malaysia)
HOSE (Vietnam)

### Africa / Middle East
JSE (South Africa)
EGX (Egypt)
TASE (Israel)
DFM (Dubai)

### Crypto exchanges (mas comunes)
BINANCE, COINBASE, KRAKEN, BITSTAMP, OKX, BYBIT, GEMINI, BITTREX, HUOBI,
BITMEX, BITFINEX, POLONIEX, KUCOIN

### Forex / Broker feeds
FX, OANDA, FX_IDC, SAXO, FXCM, NASDAQ:FOREX

### Indices / sintéticos
INDEX (sintetico TradingView)
TVC (TradingView Calculated)
DJ (Dow Jones)
CBOE (CBOE indices)

---

## Apendice: descubrir exchanges nuevos

Para descubrir exchanges no listados:

```python
# Listar todos los exchanges distintos para un country
from fetch_tradingview import screen
data = screen(
    filter_=[{"left": "country", "operation": "equal", "right": "Japan"}],
    columns=["name", "exchange"],
    limit=5000,
)
exchanges = sorted(set(item["exchange"] for item in data["data"]))
```
