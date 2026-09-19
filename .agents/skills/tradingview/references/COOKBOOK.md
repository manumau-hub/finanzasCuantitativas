# Cookbook — Casos de Uso Practicos

> Coleccion de recetas listas para copy-paste. Cada una usa el CLI
> `fetch_tradingview.py` o la API directa Python.

---

## Indice

### Quote y tecnicos
1. [Quote rapido de un stock](#1-quote-rapido-de-un-stock)
2. [Quote extendido con indicadores](#2-quote-extendido-con-indicadores)
3. [Solo indicadores tecnicos](#3-solo-indicadores-tecnicos)
4. [Solo pivots](#4-solo-pivots)
5. [Solo performance/returns historicos](#5-solo-performancereturns-historicos)
6. [Rating BUY/SELL agregado de TradingView](#6-rating-buysell-agregado-de-tradingview)

### Financials
7. [Income statement / balance / cash flow](#7-income-statement--balance--cash-flow)
8. [Comparar ratios entre 3 empresas](#8-comparar-ratios-entre-3-empresas)
9. [Earnings calendar](#9-earnings-calendar)
10. [Price targets de analistas](#10-price-targets-de-analistas)
11. [Dividendos](#11-dividendos)
12. [Short interest y ownership](#12-short-interest-y-ownership)

### Screening
13. [Top stocks US por market cap](#13-top-stocks-us-por-market-cap)
14. [Stocks oversold (RSI < 30)](#14-stocks-oversold-rsi--30)
15. [Stocks con golden cross hoy](#15-stocks-con-golden-cross-hoy)
16. [Stocks con high dividend yield](#16-stocks-con-high-dividend-yield)
17. [Stocks que reportan esta semana](#17-stocks-que-reportan-esta-semana)
18. [Empresas argentinas en cualquier mercado](#18-empresas-argentinas-en-cualquier-mercado)
19. [Top criptos por market cap](#19-top-criptos-por-market-cap)
20. [Listado completo de un sector](#20-listado-completo-de-un-sector)

### Symbol Search
21. [Resolver ticker desde nombre empresa](#21-resolver-ticker-desde-nombre-empresa)
22. [Joinear con SEC EDGAR via CIK](#22-joinear-con-sec-edgar-via-cik)
23. [Listar todas las ediciones de un ticker globalmente](#23-listar-todas-las-ediciones-de-un-ticker-globalmente)

### News
24. [Headlines de un stock](#24-headlines-de-un-stock)
25. [Headlines globales del mercado](#25-headlines-globales-del-mercado)
26. [Aggregar news de varios tickers](#26-aggregar-news-de-varios-tickers)
27. [Filtrar news por provider](#27-filtrar-news-por-provider)
28. [Detalle completo de una noticia](#28-detalle-completo-de-una-noticia)

### Pipelines
29. [Pipeline search → quote → news](#29-pipeline-search--quote--news)
30. [Quote completo todo-en-uno](#30-quote-completo-todo-en-uno)

---

## 1. Quote rapido de un stock

```bash
py fetch_tradingview.py quote NASDAQ:GGAL -q
```

```python
from fetch_tradingview import quote
q = quote("NASDAQ:GGAL")
g = q["data"][0]
print(f"{g['name']} {g['close']} ({g['change']:+.2f}%)")
```

---

## 2. Quote extendido con indicadores

```bash
py fetch_tradingview.py quote-extended NASDAQ:AAPL -q
```

Devuelve ~30 columnas: precio + market cap + P/E + EPS + dividend yield +
ratings + RSI + MACD + ADX + EMA + 52w high/low + beta + sector.

---

## 3. Solo indicadores tecnicos

```bash
py fetch_tradingview.py technicals NASDAQ:GGAL -q
```

```python
from fetch_tradingview import technicals
t = technicals("NASDAQ:GGAL")["data"][0]
print(f"RSI: {t['RSI']:.2f}")
print(f"MACD: {t['MACD.macd']:.4f} vs Signal: {t['MACD.signal']:.4f}")
print(f"EMA50: {t['EMA50']:.2f}, EMA200: {t['EMA200']:.2f}")
print(f"Rating: {t['Recommend.All']:+.3f}  (1=STRONG_BUY, -1=STRONG_SELL)")
```

---

## 4. Solo pivots

```bash
py fetch_tradingview.py pivots NASDAQ:AAPL -q
```

```python
from fetch_tradingview import pivots
p = pivots("NASDAQ:AAPL")["data"][0]
close = p["close"]
print(f"R3: {p['Pivot.M.Classic.R3']:.2f}")
print(f"R2: {p['Pivot.M.Classic.R2']:.2f}")
print(f"R1: {p['Pivot.M.Classic.R1']:.2f}")
print(f"P:  {p['Pivot.M.Classic.Middle']:.2f}  <- pivot")
print(f"=== CLOSE: {close:.2f} ===")
print(f"S1: {p['Pivot.M.Classic.S1']:.2f}")
print(f"S2: {p['Pivot.M.Classic.S2']:.2f}")
print(f"S3: {p['Pivot.M.Classic.S3']:.2f}")
```

---

## 5. Solo performance/returns historicos

```bash
py fetch_tradingview.py performance NYSE:JPM -q
```

```python
from fetch_tradingview import performance
p = performance("NYSE:JPM")["data"][0]
for period in ["W", "1M", "3M", "6M", "Y", "YTD", "5Y", "All"]:
    val = p.get(f"Perf.{period}")
    if val is not None:
        print(f"  {period:5s}: {val:+.2f}%")
```

---

## 6. Rating BUY/SELL agregado de TradingView

```bash
py fetch_tradingview.py technicals NASDAQ:NVDA -q
```

```python
from fetch_tradingview import technicals, recommend_label

t = technicals("NASDAQ:NVDA")["data"][0]
print(f"Overall:   {recommend_label(t['Recommend.All']):12s}  ({t['Recommend.All']:+.3f})")
print(f"MAs:       {recommend_label(t['Recommend.MA']):12s}  ({t['Recommend.MA']:+.3f})")
print(f"Oscilators:{recommend_label(t['Recommend.Other']):12s}  ({t['Recommend.Other']:+.3f})")
```

---

## 7. Income statement / balance / cash flow

```bash
py fetch_tradingview.py financials NASDAQ:AAPL -q
```

Devuelve ~35 columnas con balance + income + cashflow + ratios + growth.

```python
from fetch_tradingview import financials
f = financials("NASDAQ:AAPL")["data"][0]
print(f"Revenue:     ${f['total_revenue']/1e9:.1f}B")
print(f"Net income:  ${f['net_income']/1e9:.1f}B")
print(f"EBITDA:      ${f['ebitda']/1e9:.1f}B")
print(f"FCF:         ${f['free_cash_flow']/1e9:.1f}B")
print(f"Net margin:  {f['net_margin']:.1f}%")
print(f"ROE:         {f['return_on_equity']:.1f}%")
print(f"D/E:         {f['debt_to_equity']:.2f}")
```

---

## 8. Comparar ratios entre 3 empresas

```python
from fetch_tradingview import scanner_scan

cols = [
    "name", "description", "market_cap_basic",
    "price_earnings_ttm", "price_book", "return_on_equity",
    "operating_margin", "net_margin", "debt_to_equity",
    "dividend_yield_recent",
]
data = scanner_scan(
    symbols=["NASDAQ:GGAL", "NYSE:BMA", "NYSE:BBAR"],
    columns=cols,
)

import json
print(f"{'Ticker':12} {'P/E':>7} {'P/B':>7} {'ROE%':>7} {'NetMrg%':>8} {'D/E':>6} {'DivY%':>6}")
for it in data["data"]:
    print(f"{it['symbol']:12} {it['price_earnings_ttm']:7.2f} {it['price_book']:7.2f} "
          f"{it['return_on_equity']:7.1f} {it['net_margin']:8.1f} "
          f"{it['debt_to_equity']:6.2f} {it['dividend_yield_recent']:6.2f}")
```

---

## 9. Earnings calendar

```bash
py fetch_tradingview.py earnings NASDAQ:GGAL -q
```

```python
from datetime import datetime, timezone
from fetch_tradingview import earnings

e = earnings("NASDAQ:GGAL")["data"][0]
next_ts = e["earnings_release_next_date"]
if next_ts:
    next_dt = datetime.fromtimestamp(next_ts, tz=timezone.utc)
    print(f"Next earnings: {next_dt.strftime('%Y-%m-%d')}")
    print(f"Forecast EPS:  {e['earnings_per_share_forecast_next_fq']}")
    print(f"Forecast Rev:  ${e['revenue_forecast_next_fq']/1e6:.1f}M")
```

---

## 10. Price targets de analistas

```bash
py fetch_tradingview.py targets NASDAQ:NVDA -q
```

```python
from fetch_tradingview import targets, quote

t = targets("NASDAQ:NVDA")["data"][0]
current = t["close"]
avg = t["price_target_average"]
upside = (avg / current - 1) * 100 if (current and avg) else None

print(f"Current:  ${current:.2f}")
print(f"Avg PT:   ${avg:.2f}")
print(f"High PT:  ${t['price_target_high']:.2f}")
print(f"Low PT:   ${t['price_target_low']:.2f}")
print(f"Upside:   {upside:+.1f}%")
print(f"Analysts: {t['number_of_analyst_opinions']}")
print(f"Buy: {t['recommendation_buy']} | Hold: {t['recommendation_hold']} | Sell: {t['recommendation_sell']}")
```

---

## 11. Dividendos

```bash
py fetch_tradingview.py dividends NYSE:KO -q
```

```python
from fetch_tradingview import dividends
d = dividends("NYSE:KO")["data"][0]
print(f"Dividend yield (recent):    {d['dividend_yield_recent']:.2f}%")
print(f"Dividend yield (TTM):       {d['dividends_yield']:.2f}%")
print(f"DPS anual:                  ${d['dps_common_stock_prim_issue_fy']:.2f}")
print(f"Payout ratio:               {d['payout_ratio_fy']:.1f}%")
print(f"Años consecutivos pagando:  {d['continuous_dividend_payout']}")
print(f"Años consecutivos creciendo: {d['continuous_dividend_growth']}")
```

---

## 12. Short interest y ownership

```bash
py fetch_tradingview.py ownership NASDAQ:NVDA -q
```

```python
from fetch_tradingview import ownership
o = ownership("NASDAQ:NVDA")["data"][0]
print(f"Market cap:        ${o['market_cap_basic']/1e9:.1f}B")
print(f"Float shares:      {o['float_shares_outstanding']/1e9:.2f}B")
print(f"Inst. ownership:   {o['shares_owned_institutions']:.1f}%")
print(f"Insider ownership: {o['shares_owned_insiders']:.1f}%")
print(f"Short interest:    {o['short_interest_percent']:.2f}%")
print(f"Days to cover:     {o['days_to_cover_short_interest']:.1f}")
```

---

## 13. Top stocks US por market cap

```bash
py fetch_tradingview.py screen --filter '[["country","equal","United States"],["type","equal","stock"]]' --sort market_cap_basic:desc --limit 10 -q
```

```python
from fetch_tradingview import screen
top = screen(
    filter_=[
        {"left": "country", "operation": "equal", "right": "United States"},
        {"left": "type", "operation": "equal", "right": "stock"},
    ],
    sort={"sortBy": "market_cap_basic", "sortOrder": "desc"},
    limit=10,
)
for item in top["data"]:
    print(f"{item['symbol']:18} ${item['market_cap_basic']/1e9:>8.1f}B  {item['name']:8} {item['description'][:50]}")
```

---

## 14. Stocks oversold (RSI < 30)

```bash
py fetch_tradingview.py screen \
  --filter '[["type","equal","stock"],["country","equal","United States"],["RSI","less",30],["market_cap_basic","greater",10000000000]]' \
  --columns "name,description,close,RSI,Recommend.All" \
  --sort RSI:asc \
  --limit 20 -q
```

---

## 15. Stocks con golden cross hoy

```bash
py fetch_tradingview.py screen \
  --filter '[["SMA50","crosses_above","SMA200"],["country","equal","United States"]]' \
  --columns "name,close,SMA50,SMA200,Recommend.All" \
  --limit 30 -q
```

---

## 16. Stocks con high dividend yield

```bash
py fetch_tradingview.py screen \
  --filter '[["dividend_yield_recent","greater",5],["type","equal","stock"],["market_cap_basic","greater",1000000000]]' \
  --columns "name,description,close,dividend_yield_recent,payout_ratio_fy,sector" \
  --sort dividend_yield_recent:desc \
  --limit 30 -q
```

---

## 17. Stocks que reportan esta semana

```python
from datetime import datetime, timezone, timedelta
from fetch_tradingview import screen

now = int(datetime.now(tz=timezone.utc).timestamp())
week_later = now + 7 * 86400

data = screen(
    filter_=[
        {"left": "earnings_release_next_date", "operation": "in_range", "right": [now, week_later]},
        {"left": "type", "operation": "equal", "right": "stock"},
        {"left": "market_cap_basic", "operation": "greater", "right": 10_000_000_000},
    ],
    columns=[
        "name", "description", "earnings_release_next_date",
        "earnings_per_share_forecast_next_fq", "market_cap_basic",
    ],
    sort={"sortBy": "earnings_release_next_date", "sortOrder": "asc"},
    limit=50,
)
for it in data["data"]:
    dt = datetime.fromtimestamp(it["earnings_release_next_date"], tz=timezone.utc)
    print(f"{dt.strftime('%a %m-%d')}  {it['symbol']:15}  est EPS ${it['earnings_per_share_forecast_next_fq']:.2f}")
```

---

## 18. Empresas argentinas en cualquier mercado

```bash
py fetch_tradingview.py country Argentina --limit 30 -q
```

Devuelve empresas argentinas listadas en NASDAQ, NYSE, BCBA, BMV (CEDEARs),
BMFBOVESPA (BDRs), etc.

---

## 19. Top criptos por market cap

```bash
py fetch_tradingview.py market crypto --limit 20 -q
```

---

## 20. Listado completo de un sector

```bash
py fetch_tradingview.py sector Finance --market america --limit 50 -q
```

```python
from fetch_tradingview import by_sector
data = by_sector("Finance", market="america", limit=100)
for it in data["data"][:20]:
    print(f"{it['symbol']:15} {it['market_cap_basic']/1e9:>8.1f}B  {it['name']}")
```

---

## 21. Resolver ticker desde nombre empresa

```bash
py fetch_tradingview.py search "Apple" --type stocks -q
```

```python
from fetch_tradingview import symbol_search
results = symbol_search("Apple", search_type="stocks")
for s in results["symbols"][:5]:
    print(f"{s['exchange']:10}:{s['symbol']:8}  {s['description'][:60]}")
```

---

## 22. Joinear con SEC EDGAR via CIK

```python
import requests
from fetch_tradingview import symbol_search

# 1. Buscar el CIK
results = symbol_search("GGAL", search_type="stocks")
nasdaq = next((s for s in results["symbols"] if s["exchange"] == "NASDAQ"), None)
cik = nasdaq["cik_code"]
print(f"CIK: {cik}")

# 2. Fetch filings de SEC EDGAR (otro skill)
url = f"https://data.sec.gov/submissions/CIK{cik}.json"
data = requests.get(url, headers={"User-Agent": "research test@example.com"}).json()
print(f"Empresa: {data['name']}")
print(f"Last filings: {data['filings']['recent']['form'][:5]}")
```

---

## 23. Listar todas las ediciones de un ticker globalmente

```python
from fetch_tradingview import symbol_search
results = symbol_search("AAPL", search_type="stocks")
for s in results["symbols"]:
    print(f"{s['exchange']:12} {s['symbol']:8} {s['currency_code']:5} {s['description'][:60]}")
# Imprime: NASDAQ:AAPL (USD), XETR:APC (EUR), BMV:AAPL (MXN), LSE:0R2V (GBP), etc.
```

---

## 24. Headlines de un stock

```bash
py fetch_tradingview.py news NASDAQ:AAPL -q
```

```python
from datetime import datetime, timezone
from fetch_tradingview import news_by_symbol

items = news_by_symbol("NASDAQ:AAPL")["items"]
for it in items[:10]:
    dt = datetime.fromtimestamp(it["published"], tz=timezone.utc)
    print(f"[{dt.strftime('%m-%d %H:%M')}] [{it['source'][:15]:15}] {it['title']}")
```

---

## 25. Headlines globales del mercado

```bash
py fetch_tradingview.py news-global -q
```

---

## 26. Aggregar news de varios tickers

```python
from fetch_tradingview import news_by_symbol

symbols = ["NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:GOOGL", "NASDAQ:AMZN", "NASDAQ:META"]
all_items = []
for s in symbols:
    items = news_by_symbol(s)["items"]
    all_items.extend(items)

# Dedupe
seen = set()
unique = [it for it in all_items if not (it["id"] in seen or seen.add(it["id"]))]

# Sort
unique.sort(key=lambda x: x["published"], reverse=True)
print(f"Total unique news: {len(unique)}")
```

---

## 27. Filtrar news por provider

```python
from fetch_tradingview import news_by_symbol
items = news_by_symbol("NASDAQ:AAPL")["items"]
dj_only = [it for it in items if it["provider"] == "dow-jones"]
reuters_only = [it for it in items if it["provider"] == "reuters"]
print(f"DJ items: {len(dj_only)}")
print(f"Reuters items: {len(reuters_only)}")
```

---

## 28. Detalle completo de una noticia

```bash
py fetch_tradingview.py story "/news/DJN_DN20260604009289:0/" -q
```

```python
from fetch_tradingview import news_by_symbol, news_story

items = news_by_symbol("NASDAQ:AAPL")["items"]
first = items[0]
detail = news_story(first["storyPath"])
print(f"Title: {detail['title']}")
print(f"Body:  {detail['body'][:500]}...")
```

---

## 29. Pipeline search → quote → news

```python
from fetch_tradingview import symbol_search, quote, news_by_symbol

# 1. Buscar
match = symbol_search("Apple", search_type="stocks")["symbols"][0]
ticker = f"{match['exchange']}:{match['symbol']}"
print(f"Resolved to: {ticker}")

# 2. Quote
q = quote(ticker)["data"][0]
print(f"Price: ${q['close']:.2f} ({q['change']:+.2f}%)")

# 3. News
n = news_by_symbol(ticker)["items"][:3]
for it in n:
    print(f"  - {it['title']}")
```

---

## 30. Quote completo todo-en-uno

```bash
py fetch_tradingview.py all NASDAQ:GGAL -o ggal_full.json
```

Combina **6 requests** en un solo dict:
- `quote_extended` (~30 cols con precio + ratings + indicators + valuacion)
- `technicals` (~36 cols)
- `financials` (~35 cols)
- `earnings` (~12 cols)
- `targets` (~10 cols)
- `news` (hasta 200 items)
- `_rating_label`: etiqueta humana de `Recommend.All`

```python
from fetch_tradingview import fetch_all
data = fetch_all("NASDAQ:GGAL")
print(data["_rating_label"])           # ej: "BUY"
print(data["quote_extended"]["data"][0]["close"])
print(data["targets"]["data"][0]["price_target_average"])
print(len(data["news"]["items"]))
```
