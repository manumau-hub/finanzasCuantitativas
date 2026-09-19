---
name: google-finance
description: "Datos de Google Finance via batchexecute (API RPC interna sin auth ni API key). Quote, OHLC intraday 1-min y 5-min, OHLC daily, financials masivos (income/balance/cashflow), earnings, analyst recommendations + opinions, descripcion empresa, peers, news, indices globales (Dow/S&P/NASDAQ/VIX/DAX), sectors heatmap. Cobertura mercados US (NASDAQ/NYSE) y argentinos (BCBA). ⚠️ API NO oficial — leer LIMITATIONS_TROUBLESHOOTING.md antes de uso productivo."
license: MIT
---

# Google Finance — Data via API Interna sin Auth

Skill para extraer datos de [Google Finance](https://www.google.com/finance)
via su **endpoint RPC interno `batchexecute`** descubierto por reverse
engineering — **sin API key, sin autenticacion**.

Cubre quote, OHLC historico (intraday 1-min / 5-min / daily / 6-meses),
financials masivos, earnings, analyst recommendations con opinions
individuales (Goldman, etc), descripcion empresa con address+employees,
peers, news (con thumbnails), indices globales (Dow/S&P/NASDAQ/VIX/DAX/FTSE/Nikkei)
y sectors heatmap.

---

## ⚠️ WARNINGS CRITICOS — LEER PRIMERO

> **Antes de usar este skill en cualquier escenario productivo, leer
> obligatoriamente
> [`references/LIMITATIONS_TROUBLESHOOTING.md`](./references/LIMITATIONS_TROUBLESHOOTING.md).**

### TL;DR de los 4 warnings principales

1. **🚨 API NO oficial** — Google puede renombrar RPCs, cambiar layouts,
   agregar auth o cerrar el endpoint sin aviso.
2. **🚨 Layouts SIN keys** — Los responses son arrays posicionales. Si
   Google reordena campos, vas a leer mal sin error visible.
3. **🚨 Rate limiting muy agresivo** — > 5 req/s puede bloquear tu IP por
   horas. Recomendado: sleep ≥ 0.5s entre requests.
4. **🚨 Sin warranty de continuidad** — Si construis algo importante,
   tener fallback con otro provider (Yahoo Finance, TradingView, Finnhub).

### Cuando NO usar este skill

- Trading en produccion con decisiones criticas (usar feeds oficiales).
- Aplicaciones publicas que sirvan los datos a usuarios.
- Volumen > 10k requests/dia (riesgo de bloqueo permanente de IP).
- Redistribuir los datos como propios (terminos de uso de Google).

### Cuando SI usar este skill

- Investigacion personal y prototipos.
- Backtest con cache local.
- Analisis comparativo cruzado con otros providers.
- Casos donde los datos UNICOS de Google son criticos (intraday 1-min
  gratis, detalle individual de analyst opinions).

---

## 🚀 Quick start

```bash
# Quote basico
py scripts/fetch_gfinance.py quote GGAL:NASDAQ
py scripts/fetch_gfinance.py quote AAPL:NASDAQ
py scripts/fetch_gfinance.py quote GGAL:BCBA       # mercado argentino

# Intraday del dia actual
py scripts/fetch_gfinance.py intraday-5min AAPL:NASDAQ
py scripts/fetch_gfinance.py intraday-1min GGAL:NASDAQ

# Daily historico
py scripts/fetch_gfinance.py daily-6m AAPL:NASDAQ

# Indices globales (Dow, S&P, NASDAQ, VIX, DAX, FTSE, Nikkei...)
py scripts/fetch_gfinance.py indices

# Analyst recommendations + opinions individuales
py scripts/fetch_gfinance.py analysts NVDA:NASDAQ

# Todo en uno (6 requests pipelinadas)
py scripts/fetch_gfinance.py all GGAL:NASDAQ
```

---

## Estructura del skill

```
skills/google-finance/
├── SKILL.md                                # Este archivo
├── references/                             # 5 documentos
│   ├── REFERENCE.md                        # Overview general + batchexecute
│   ├── RPC_IDS.md                          # Catalogo de los 14+ RPC IDs
│   ├── RESPONSE_FORMAT.md                  # Parser deep dive del wrb.fr protocol
│   ├── LIMITATIONS_TROUBLESHOOTING.md      # ⚠️ Warnings, plan B, debugging
│   └── COOKBOOK.md                         # 25 recetas listas
├── assets/                                 # 3 archivos JSON
│   ├── rpc_ids.json                        # Catalogo estructurado de RPCs + args
│   ├── chunk_layouts.json                  # Layouts posicionales de los arrays
│   └── consent_cookies.json                # Cookies de bypass del consent
└── scripts/
    └── fetch_gfinance.py                   # Script principal — 19 modos CLI
```

---

## 19 modos CLI disponibles

### Por simbolo

| Modo | Data | RPC ID |
|------|------|--------|
| `quote SYM` | Precio + change + currency + market hours | `gCvqoe` |
| `quote-full SYM` | Quote + industry + market cap + volume | `dlNq8b` |
| `description SYM` | Descripcion + address + employees + ratios + URLs | `JL8oKc` |
| `peers SYM` | Related stocks (default 4, controlable con `--peers-count`) | `SICF5d` |
| `analysts SYM` | Recommendations summary + opinions individuales | `YTM9q` |
| `earnings SYM` | Earnings history multi-period | `XxQsbd` |
| `technicals SYM` | Ratings tecnicos (similar a TradingView Recommend.*) | `gXxkFd` |
| `financials SYM` | Income + balance + cashflow ~22 KB multi-period | `Pr8h2e` |
| `intraday-1min SYM` | OHLC 1-min del dia actual (~30 KB) | `c2u4wc` |
| `intraday-5min SYM` | OHLC 5-min con OHLC completo (~5 KB) | `c2u4wc` |
| `daily SYM` | OHLC diario ultimo mes (~22 dias) | `c2u4wc` |
| `daily-6m SYM` | OHLC diario ultimos ~6 meses | `c2u4wc` |
| `news SYM` | News especificas del simbolo | `kA4MVd` |
| `news-related SYM` | News globales (con related symbols del query) | `kA4MVd` |

### Globales (sin simbolo)

| Modo | Data | RPC ID |
|------|------|--------|
| `indices` | Indices globales: Dow, S&P, NASDAQ, VIX, DAX, FTSE, Nikkei, etc | `hgueg` |
| `sectors` | Sectors equity heatmap (Health Care, Tech, etc) | `vNewwe` |

### Catalogos locales (sin HTTP)

| Modo | Data |
|------|------|
| `rpcs` | Catalogo de RPC IDs con args templates y descripciones |
| `layouts` | Layouts posicionales de los arrays anidados |
| `cookies` | Cookies de bypass del consent screen |

### Combinado

| Modo | Data |
|------|------|
| `all SYM` | quote + description + analysts + financials + daily + news (6 requests) |

---

## Formato de simbolos

| Donde | Formato | Ejemplos |
|-------|---------|----------|
| Tickers US | `TICKER:NASDAQ` o `TICKER:NYSE` | `AAPL:NASDAQ`, `JPM:NYSE` |
| ADRs argentinas | `TICKER:NASDAQ` o `TICKER:NYSE` | `GGAL:NASDAQ`, `BBAR:NYSE` |
| **Tickers BCBA** (locales argentinas) | `TICKER:BCBA` | `GGAL:BCBA`, `YPFD:BCBA` |
| Brazil B3 | `TICKER:BMFBOVESPA` | `PETR4:BMFBOVESPA` |
| Spain BME | `TICKER:BME` | `SAN:BME` |
| Germany Xetra | `TICKER:XETR` | `SAP:XETR` |
| Indices | `IDX:INDEXSP/DJX/NASDAQ/CBOE` | `.INX:INDEXSP`, `.DJI:INDEXDJX` |

> El script tambien acepta el orden invertido (`NASDAQ:GGAL`) — auto-detecta
> cual es el exchange. Pero el formato canonical de Google es `TICKER:EXCHANGE`.

---

## Diferenciales unicos vs otros skills del repo

| Feature | Google Finance | TradingView | Yahoo | Finnhub |
|---------|:--------------:|:-----------:|:-----:|:-------:|
| Sin auth | ✅ | ✅ | ✅ | Freemium |
| **OHLC intraday 1-min publico gratis** | ✅ **UNICO** | ❌ (paid) | ⚠️ limited | ⚠️ paid |
| **OHLC 5-min completo** | ✅ | ❌ | ⚠️ | ⚠️ |
| **Indices globales en 1 call** (Dow+S&P+NASDAQ+VIX+DAX+FTSE+Nikkei...) | ✅ **UNICO** | ⚠️ uno por uno | ⚠️ | ⚠️ |
| **Detalle individual de analyst opinions** (nombre, firm, target, fecha) | ✅ **UNICO** | ⚠️ solo agregado | ⚠️ | ✅ |
| **Sectors heatmap** | ✅ | ⚠️ | ❌ | ❌ |
| **Descripcion empresa** con address fisico + employees | ✅ **UNICO** | ⚠️ | ⚠️ | ✅ |
| Quote delayed | ✅ | ✅ | ✅ | ✅ |
| Financials | ✅ (~22 KB) | ✅ | ✅ | ✅ |
| News con thumbnails | ✅ | ✅ | ✅ | ✅ |

### Cuando usar Google Finance > TradingView

- Necesitas OHLC intraday 1-min sin pagar.
- Necesitas detalle individual de opinions por analista con firma/target/fecha.
- Necesitas el address fisico de una empresa argentina.
- Necesitas indices globales (Dow+S&P+NASDAQ+VIX+DAX+FTSE+Nikkei) en una sola call.

### Cuando usar TradingView > Google Finance

- Necesitas screener masivo con filtros tipo SQL.
- Necesitas ISIN/CUSIP/CIK del simbolo (Symbol Search v3).
- Necesitas indicadores tecnicos pre-calculados (RSI/MACD/EMAs/pivots).
- Necesitas robustez — TV es mucho mas estable que Google Finance.

---

## Consideraciones tecnicas

### Endpoint

```
POST https://www.google.com/finance/beta/_/FinHubUi/data/batchexecute?rpcids={RPC_ID}
```

### Headers requeridos

Ya configurados en el script:

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "X-Same-Domain": "1",           # CRITICO
    "Origin": "https://www.google.com",
    "Referer": "https://www.google.com/finance/...",
}
```

### Cookies de bypass

El script las pasa automaticamente:

```python
COOKIES = {
    "CONSENT": "PENDING+999",
    "SOCS": "CAESHAgBEhJnd3NfMjAyNTAxMjMtMF9SQzMaAmVuIAEaBgiAvLW8Bg",
}
```

Si dejan de funcionar, ver [LIMITATIONS_TROUBLESHOOTING.md seccion 6](./references/LIMITATIONS_TROUBLESHOOTING.md#6-que-hacer-si-la-api-deja-de-funcionar)
para capturar cookies frescas.

### Response format (wrb.fr)

Los responses usan el protocolo **wrb.fr** de Google (XSSI prefix + JSON
serializado doble). El script tiene un `parse_wrbfr()` que lo maneja.
Detalles en [RESPONSE_FORMAT.md](./references/RESPONSE_FORMAT.md).

### Rate limiting

⚠️ **Aggressive**. Recomendado:
- Sleep ≥ 0.5s entre requests.
- < 1k requests/dia para no triggear bloqueo IP.
- NO usar desde CI sin precauciones (cloud IPs en blacklist).

### Output

- Por defecto: JSON al stdout.
- `-o archivo.json`: guarda a archivo (UTF-8, `ensure_ascii=False`).
- `-q`: modo silencioso (sin logs INFO).
- `--raw`: retorna response raw sin extraer del array wrb.fr.

### Manejo de errores

El script captura `requests.HTTPError` y muestra el body para debugging.
Si el endpoint deja de funcionar, te apunta a `LIMITATIONS_TROUBLESHOOTING.md`.

---

## Casos comunes — recetas rapidas

> **25 recetas completas en [COOKBOOK.md](./references/COOKBOOK.md).**

```bash
# Quote rapido
py scripts/fetch_gfinance.py quote GGAL:NASDAQ -q

# Stock argentino BCBA
py scripts/fetch_gfinance.py quote GGAL:BCBA -q

# Indices globales del dia
py scripts/fetch_gfinance.py indices -q

# Intraday 5-min con OHLC completo
py scripts/fetch_gfinance.py intraday-5min AAPL:NASDAQ -o aapl_5min.json

# Daily ultimos 6 meses
py scripts/fetch_gfinance.py daily-6m AAPL:NASDAQ -o aapl_6m.json

# Analyst recommendations + opinions individuales
py scripts/fetch_gfinance.py analysts NVDA:NASDAQ -q

# Comparar empresa con peers
py scripts/fetch_gfinance.py peers GGAL:NASDAQ --peers-count 5 -q

# Todo-en-uno (snapshot completo)
py scripts/fetch_gfinance.py all GGAL:NASDAQ -o ggal_complete.json
```

---

## Documentacion completa

| Documento | Contenido |
|-----------|-----------|
| [`references/REFERENCE.md`](./references/REFERENCE.md) | Overview general + batchexecute deep dive |
| [`references/RPC_IDS.md`](./references/RPC_IDS.md) | Catalogo detallado de los 14+ RPC IDs con args + outputs |
| [`references/RESPONSE_FORMAT.md`](./references/RESPONSE_FORMAT.md) | Parser deep dive del wrb.fr (XSSI, doble JSON, edge cases) |
| [`references/LIMITATIONS_TROUBLESHOOTING.md`](./references/LIMITATIONS_TROUBLESHOOTING.md) | **⚠️ Warnings, debugging, plan B con providers alternativos** |
| [`references/COOKBOOK.md`](./references/COOKBOOK.md) | **25 recetas listas para copy-paste** |
| [`assets/rpc_ids.json`](./assets/rpc_ids.json) | Catalogo de RPCs con args templates y descripciones |
| [`assets/chunk_layouts.json`](./assets/chunk_layouts.json) | Layouts posicionales de cada array (que indice = que campo) |
| [`assets/consent_cookies.json`](./assets/consent_cookies.json) | Cookies de bypass del consent screen |

---

## Inspiracion y atribuciones

Este skill fue construido a partir de research del HTML de
`google.com/finance/beta/quote/GGAL:NASDAQ`, identificando los chunks
`AF_initDataCallback` con su sistema "Wiz" (mismo que usa Search, Maps,
Translate). El protocolo wrb.fr es publico y bien documentado por la
comunidad (no por Google).

Implementaciones similares en otros lenguajes:
- `google-finance-quotes` (Node.js) — usa el mismo endpoint
- `mfinance` (Python, distinto enfoque)
- Multiples proyectos OSS de scraping de finance.google.com

Este skill se distingue por:
1. **24 modos CLI** sobre 14+ RPC IDs distintos.
2. **Documentacion exhaustiva** de los warnings y plan B.
3. **Catalogo estructurado** de RPCs + layouts posicionales en assets.
4. **Parser robusto** del wrb.fr con manejo de todos los edge cases.
