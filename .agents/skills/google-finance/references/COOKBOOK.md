# Cookbook — Recetas Listas para Copy-Paste

> Coleccion de recetas para los casos de uso comunes del skill `google-finance`.
> Cada receta usa el CLI `fetch_gfinance.py` o la API directa Python.

---

## Indice

### Quote y precios
1. [Quote rapido de un stock](#1-quote-rapido-de-un-stock)
2. [Quote de stock argentino BCBA](#2-quote-de-stock-argentino-bcba)
3. [Quote enriquecido con industry y volume](#3-quote-enriquecido-con-industry-y-volume)
4. [Indices globales (Dow, S&P, NASDAQ, VIX, DAX)](#4-indices-globales-dow-sp-nasdaq-vix-dax)
5. [Sectors heatmap](#5-sectors-heatmap)

### Historico OHLC
6. [Intraday 1-min del dia](#6-intraday-1-min-del-dia)
7. [Intraday 5-min con OHLC completo](#7-intraday-5-min-con-ohlc-completo)
8. [Daily ultimo mes](#8-daily-ultimo-mes)
9. [Daily ultimos 6 meses](#9-daily-ultimos-6-meses)

### Empresa
10. [Descripcion + employees + market cap](#10-descripcion--employees--market-cap)
11. [Address y website de la empresa](#11-address-y-website-de-la-empresa)
12. [Peers / related stocks](#12-peers--related-stocks)
13. [Comparar 3 empresas (multi-symbol quote)](#13-comparar-3-empresas-multi-symbol-quote)

### Analyst / earnings
14. [Analyst recommendations summary](#14-analyst-recommendations-summary)
15. [Listado de opinions individuales por analista](#15-listado-de-opinions-individuales-por-analista)
16. [Earnings history](#16-earnings-history)

### Financials
17. [Financials raw multi-period](#17-financials-raw-multi-period)
18. [Pipeline financials → migrar a sec-data si es US](#18-pipeline-financials--migrar-a-sec-data-si-es-us)

### News
19. [News especificas del simbolo](#19-news-especificas-del-simbolo)
20. [News globales del mercado](#20-news-globales-del-mercado)
21. [News con thumbnail y deduplicacion](#21-news-con-thumbnail-y-deduplicacion)

### Pipelines
22. [Quote + technicals en paralelo](#22-quote--technicals-en-paralelo)
23. [Todo en uno (all)](#23-todo-en-uno-all)
24. [Parser de quote_array → dict con keys](#24-parser-de-quote_array--dict-con-keys)
25. [Conversion timestamps a fechas](#25-conversion-timestamps-a-fechas)

---

## 1. Quote rapido de un stock

```bash
py scripts/fetch_gfinance.py quote GGAL:NASDAQ -q
py scripts/fetch_gfinance.py quote AAPL:NASDAQ -q
py scripts/fetch_gfinance.py quote JPM:NYSE -q
```

```python
from fetch_gfinance import quote, parse_symbol

data = quote("AAPL:NASDAQ")
row = data[0][0]
name = row[2]
price = row[5][0]
change_pct = row[5][2]
prev_close = row[7]
currency = row[4]
print(f"{name}: {currency} {price:.2f} ({change_pct:+.2f}%) prev: {prev_close:.2f}")
# → Apple Inc: USD 311.23 (+0.31%) prev: 310.26
```

---

## 2. Quote de stock argentino BCBA

```bash
py scripts/fetch_gfinance.py quote GGAL:BCBA -q
py scripts/fetch_gfinance.py quote YPFD:BCBA -q
```

```python
data = quote("GGAL:BCBA")
row = data[0][0]
print(f"{row[2]}: {row[4]} {row[5][0]}")
# → Grupo Financiero Galicia SA: ARS 7350
```

---

## 3. Quote enriquecido con industry y volume

```bash
py scripts/fetch_gfinance.py quote-full AAPL:NASDAQ -q
```

```python
from fetch_gfinance import quote_full

data = quote_full("AAPL:NASDAQ")
row = data[0][0]
print(f"Industry:    {row[19]}")    # 'Bank', 'Software', etc.
print(f"Market cap:  ${row[16]:,.0f}")
print(f"Volume:      {row[17]:,}")
```

---

## 4. Indices globales (Dow, S&P, NASDAQ, VIX, DAX)

```bash
py scripts/fetch_gfinance.py indices -q
```

```python
from fetch_gfinance import indices

data = indices()
# Estructura: [[regions: [[null, [indices_list], region_name]]]]
for region in data[0]:
    region_name = region[2] if len(region) > 2 else "?"
    indices_list = region[1]
    for idx in indices_list[1] if len(indices_list) > 1 else []:
        # Cada idx es un quote_array
        if isinstance(idx, list) and len(idx) > 1 and idx[1]:
            name = idx[2]
            price = idx[5][0]
            change_pct = idx[5][2]
            print(f"  {name:35s} {price:>12,.2f} ({change_pct:+.2f}%)")
```

---

## 5. Sectors heatmap

```bash
py scripts/fetch_gfinance.py sectors -q
```

```python
from fetch_gfinance import sectors

data = sectors()
# Sectors array tiene cada uno: [..., name, change, ...]
for sect in data[0][0][3]:
    name = sect[15]      # "Health Care", "Energy", etc.
    change_pct = sect[11]  # cambio %
    print(f"  {name:30s} {change_pct:+.2f}%")
```

---

## 6. Intraday 1-min del dia

```bash
py scripts/fetch_gfinance.py intraday-1min GGAL:NASDAQ -q
py scripts/fetch_gfinance.py intraday-1min AAPL:NASDAQ -o aapl_1min.json
```

```python
from fetch_gfinance import intraday_1min

data = intraday_1min("AAPL:NASDAQ")
# Estructura: data[0][3][0][1] = array de bars
bars = data[0][3][0][1]
for bar in bars[:5]:
    ts = bar[0]  # [year, month, day, hour, minute, ...]
    price = bar[1][0]
    volume = bar[2]
    print(f"  {ts[0]}-{ts[1]:02}-{ts[2]:02} {ts[3]:02}:{ts[4]:02}  ${price:.2f}  vol={volume:,}")
```

> ⚠️ El 1-min solo trae **close + change**, NO OHLC. Para OHLC verdadero usar 5-min.

---

## 7. Intraday 5-min con OHLC completo

```bash
py scripts/fetch_gfinance.py intraday-5min AAPL:NASDAQ -q
```

```python
from fetch_gfinance import intraday_5min

data = intraday_5min("AAPL:NASDAQ")
bars = data[0][3][0][2]  # Notar [2] en vez de [1] — distinto layout!
for bar in bars[:5]:
    open_, close, high, low, ts_iso, vol = bar
    print(f"  {ts_iso}  O:{open_:.2f}  H:{high:.2f}  L:{low:.2f}  C:{close:.2f}  vol={vol:,}")
```

---

## 8. Daily ultimo mes

```bash
py scripts/fetch_gfinance.py daily GGAL:NASDAQ -q
```

```python
from fetch_gfinance import daily

data = daily("GGAL:NASDAQ")
bars = data[0][3][0][1]  # ~22 dias
for bar in bars:
    ts = bar[0]
    close = bar[1][0]
    change_pct = bar[1][2]
    vol = bar[2]
    print(f"  {ts[0]}-{ts[1]:02}-{ts[2]:02}  ${close:.2f} ({change_pct:+.2%})  vol={vol:,}")
```

---

## 9. Daily ultimos 6 meses

```bash
py scripts/fetch_gfinance.py daily-6m AAPL:NASDAQ -o aapl_6m.json
```

```python
from fetch_gfinance import daily_6m

data = daily_6m("AAPL:NASDAQ")
bars = data[0][3][0][1]
print(f"Total bars: {len(bars)}")
# Calcular performance
first_close = bars[0][1][0]
last_close = bars[-1][1][0]
print(f"Performance 6m: {(last_close/first_close - 1) * 100:+.2f}%")
```

---

## 10. Descripcion + employees + market cap

```bash
py scripts/fetch_gfinance.py description AAPL:NASDAQ -q
```

```python
from fetch_gfinance import description

data = description("AAPL:NASDAQ")
row = data[0][0]
print(f"Short name:    {row[1]}")
print(f"Description:   {row[2][:200]}...")
print(f"Address:       {', '.join(row[3])}")
print(f"Founded:       {row[4][0] if row[4] else '?'}")
print(f"Employees:     {row[6]:,}")
print(f"Market cap:    ${row[7]:,.0f}")
print(f"Day range:     ${row[11]:.2f} - ${row[10]:.2f}")
print(f"52w range:     ${row[13]:.2f} - ${row[12]:.2f}")
print(f"Volume:        {row[14]:,}")
```

---

## 11. Address y website de la empresa

```python
from fetch_gfinance import description

data = description("GGAL:NASDAQ")
row = data[0][0]
addr = row[3]
city, region, country_full, country_code, street = addr
print(f"Address: {street}, {city}, {region}, {country_full} ({country_code})")
# Address: TTE. GRAL. JUAN D PERON 456, Buenos Aires, Buenos Aires, Argentina (AR)

website = row[22]
print(f"Website: {website}")
# Website: http://www.gfgsa.com/
```

---

## 12. Peers / related stocks

```bash
py scripts/fetch_gfinance.py peers GGAL:NASDAQ -q
py scripts/fetch_gfinance.py peers AAPL:NASDAQ --peers-count 10
```

```python
from fetch_gfinance import peers

data = peers("GGAL:NASDAQ", count=5)
peer_list = data[0]
for peer_wrapper in peer_list:
    peer = peer_wrapper[0]  # quote_array
    name = peer[2]
    ticker = ":".join(peer[1])  # ['BBAR', 'NYSE'] → 'BBAR:NYSE'
    price = peer[5][0]
    change_pct = peer[5][2]
    print(f"  {ticker:15} {name:30s} ${price:.2f} ({change_pct:+.2f}%)")
```

---

## 13. Comparar 3 empresas (multi-symbol quote)

```python
from fetch_gfinance import call_batchexecute

# Pasar multiples simbolos en el mismo args:
args = [[[None, ["AAPL", "NASDAQ"]],
         [None, ["MSFT", "NASDAQ"]],
         [None, ["GOOGL", "NASDAQ"]]], 1]
data = call_batchexecute("gCvqoe", args, sym_pair=("AAPL", "NASDAQ"))

for row in data[0]:
    name = row[2]
    price = row[5][0]
    change_pct = row[5][2]
    print(f"  {name:25s} ${price:>8.2f} ({change_pct:+.2f}%)")
```

---

## 14. Analyst recommendations summary

```bash
py scripts/fetch_gfinance.py analysts NVDA:NASDAQ -q
```

```python
from fetch_gfinance import analysts

data = analysts("NVDA:NASDAQ")
summary = data[0]
name, ccy, pt_avg, pt_high, pt_low, upside_pct, n_analysts, rating = summary[:8]
buy_counts = summary[8:13]  # [strong_buy, buy, hold, sell, strong_sell]

print(f"Company:           {name}")
print(f"Consensus rating:  {rating}")
print(f"Avg price target:  {ccy} {pt_avg:.2f}")
print(f"Range:             {pt_low:.2f} - {pt_high:.2f}")
print(f"Upside est:        {upside_pct:+.2f}%")
print(f"Num analysts:      {n_analysts}")
print(f"  Strong buy: {buy_counts[0]} | Buy: {buy_counts[1]} | "
      f"Hold: {buy_counts[2]} | Sell: {buy_counts[3]} | Strong sell: {buy_counts[4]}")
```

---

## 15. Listado de opinions individuales por analista

```python
from datetime import datetime
from fetch_gfinance import analysts

data = analysts("AAPL:NASDAQ")
opinions = data[1]
for op in opinions[:10]:
    analyst_name = op[1]
    firm = op[2]
    rating = op[3]
    date = op[4]
    target = op[21] if len(op) > 21 else None
    print(f"  [{date}] {firm:30s} {analyst_name:25s} → {rating:8s} target: ${target}")
```

---

## 16. Earnings history

```bash
py scripts/fetch_gfinance.py earnings AAPL:NASDAQ -q
```

```python
from fetch_gfinance import earnings

data = earnings("AAPL:NASDAQ")
for row in data[0][:5]:
    year = row[3]
    quarter = row[4]  # 4 = full year
    earnings_data = row[9]
    # EPS reportado tipicamente en posicion 8 del earnings_data
    eps = earnings_data[8] if earnings_data else None
    ccy = earnings_data[16] if earnings_data and len(earnings_data) > 16 else "?"
    period_end = earnings_data[17] if earnings_data and len(earnings_data) > 17 else None
    print(f"  {year} Q{quarter}: EPS {ccy} {eps} (period end: {period_end})")
```

---

## 17. Financials raw multi-period

```bash
py scripts/fetch_gfinance.py financials AAPL:NASDAQ -o aapl_fin.json
```

```python
from fetch_gfinance import financials

data = financials("AAPL:NASDAQ")
# data[0] tiene los periodos
for period in data[0][0][:3]:
    year = period[0]
    quarter = period[1]
    fin = period[2]
    revenue = fin[0]
    op_income = fin[1]
    op_margin = fin[2]
    net_income = fin[4]
    ccy = fin[16]
    period_end = fin[17]
    print(f"{year} Q{quarter} ({period_end[0]}-{period_end[1]:02}-{period_end[2]:02}):")
    print(f"  Revenue:     {ccy} {revenue:,.0f}")
    print(f"  Op income:   {ccy} {op_income:,.0f}  ({op_margin:.1f}% margin)")
    print(f"  Net income:  {ccy} {net_income:,.0f}")
```

> ⚠️ Para financials con keys (no posicional), usar `sec-data` (US) o
> `macrotrends` (global). Ver `LIMITATIONS_TROUBLESHOOTING.md` seccion 8.

---

## 18. Pipeline financials → migrar a sec-data si es US

```python
from fetch_gfinance import description

data = description("AAPL:NASDAQ")
country = data[0][0][3][3]  # country_code
if country == "US":
    print("→ Para datos US estructurados, usar el skill sec-data:")
    print("    py skills/sec-data/scripts/fetch_sec.py company AAPL")
else:
    print(f"→ Pais {country}, usar Google Finance financials raw")
```

---

## 19. News especificas del simbolo

```bash
py scripts/fetch_gfinance.py news GGAL:NASDAQ -q
py scripts/fetch_gfinance.py news AAPL:NASDAQ -q
```

```python
from datetime import datetime, timezone
from fetch_gfinance import news

data = news("AAPL:NASDAQ")
for item in data[0][:10]:
    url = item[0]
    title = item[1]
    source = item[2]
    published = datetime.fromtimestamp(item[4], tz=timezone.utc)
    print(f"[{published.strftime('%m-%d %H:%M')}] [{source}] {title[:60]}")
    print(f"  → {url}")
```

---

## 20. News globales del mercado

```bash
py scripts/fetch_gfinance.py news-related GGAL:NASDAQ -q
```

```python
from fetch_gfinance import news_related

data = news_related("AAPL:NASDAQ")
# Items globales con related symbols
for item in data[0][:5]:
    title = item[1]
    related_syms_raw = item[8] if len(item) > 8 else []
    related = []
    if related_syms_raw:
        for r in related_syms_raw[:3]:
            if isinstance(r, list) and len(r) > 1:
                ticker = ":".join(r[1])
                related.append(ticker)
    print(f"  {title[:60]}")
    print(f"     Related: {', '.join(related)}")
```

---

## 21. News con thumbnail y deduplicacion

```python
from fetch_gfinance import news, news_related

# Aggregar news de un symbol + globales relacionadas
items_local = news("AAPL:NASDAQ")[0]
items_global = news_related("AAPL:NASDAQ")[0]
all_items = items_local + items_global

# Dedupe por url
seen = set()
unique = []
for it in all_items:
    url = it[0]
    if url not in seen:
        seen.add(url)
        unique.append(it)

# Sort por published desc
unique.sort(key=lambda x: x[4], reverse=True)

print(f"Total unique news: {len(unique)}")
for it in unique[:10]:
    print(f"  [{it[2]}] {it[1][:60]}  thumb: {it[3][:80]}")
```

---

## 22. Quote + technicals en paralelo

```python
import time
from fetch_gfinance import quote, technicals

sym = "GGAL:NASDAQ"

q = quote(sym)
time.sleep(0.3)
t = technicals(sym)

q_row = q[0][0]
t_data = t[2]

print(f"Price:    ${q_row[5][0]:.2f}")
print(f"Change:   {q_row[5][2]:+.2f}%")
print(f"RSI:      {t_data[7]:.2f}")
print(f"Bull:     {t_data[4]:.4f}")
print(f"Bear:     {t_data[5]:.4f}")
```

---

## 23. Todo en uno (all)

```bash
py scripts/fetch_gfinance.py all GGAL:NASDAQ -o ggal_complete.json
```

```python
from fetch_gfinance import fetch_all

data = fetch_all("AAPL:NASDAQ")
# data tiene: quote, description, analysts, financials, daily, news
print(f"Available sections: {list(data.keys())}")
# → ['symbol', 'timestamp', 'quote', 'description', 'analysts', 'financials', 'daily', 'news']
```

---

## 24. Parser de quote_array → dict con keys

```python
from fetch_gfinance import quote

QUOTE_ARRAY_FIELDS = [
    "freebase_id", "ticker_pair", "company_name", "_flag_3",
    "currency", "price_data", "_field_6", "previous_close",
    "color_hex", "country_code", "industry_freebase_id",
    "last_update_unix", "timezone", "tz_offset_seconds",
    "freebase_id_dup", "_field_15", "after_hours_data",
    "market_open_unix", "market_close_unix", "market_session",
    "_field_20", "ticker_pair_string", "_flag_22",
    "_field_23", "_field_24", "_field_25", "is_extended_hours"
]


def quote_to_dict(quote_array):
    """Convierte un quote_array posicional a un dict con keys."""
    d = {k: v for k, v in zip(QUOTE_ARRAY_FIELDS, quote_array)}
    # Unpack price_data
    pd = d.get("price_data") or [None] * 6
    d["price"] = pd[0]
    d["change_abs"] = pd[1]
    d["change_pct"] = pd[2]
    return d


data = quote("AAPL:NASDAQ")
q = quote_to_dict(data[0][0])
print(f"Company: {q['company_name']}")
print(f"Price:   {q['currency']} {q['price']:.2f}")
print(f"Change:  {q['change_pct']:+.2f}%")
print(f"Country: {q['country_code']}")
```

---

## 25. Conversion timestamps a fechas

```python
from datetime import datetime, timezone, timedelta
from fetch_gfinance import quote

data = quote("AAPL:NASDAQ")
row = data[0][0]

# Last update
ts = row[11][0]  # unix seconds
tz_offset = row[13]  # seconds (-14400 = UTC-4 = America/New_York EDT)
tz = timezone(timedelta(seconds=tz_offset))
dt = datetime.fromtimestamp(ts, tz=tz)
print(f"Last update: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")

# Market open/close
open_ts = row[17][0]
close_ts = row[18][0]
print(f"Market open:  {datetime.fromtimestamp(open_ts, tz=tz)}")
print(f"Market close: {datetime.fromtimestamp(close_ts, tz=tz)}")
```
