# Limitaciones y Troubleshooting

> ⚠️ **LECTURA OBLIGATORIA antes de usar este skill en produccion.**
>
> Google Finance no tiene API publica oficial. Todo lo que hacemos es
> **reverse engineering** de un endpoint interno. Este documento detalla
> las limitaciones conocidas, warnings y un plan-B para cuando la API
> cambie (que pasara — la pregunta es cuando).

---

## Indice

1. [⚠️ Warnings criticos](#1-warnings-criticos)
2. [Limitaciones tecnicas](#2-limitaciones-tecnicas)
3. [Limitaciones de cobertura](#3-limitaciones-de-cobertura)
4. [Limitaciones de los datos](#4-limitaciones-de-los-datos)
5. [Problemas conocidos por modo](#5-problemas-conocidos-por-modo)
6. [Que hacer si la API deja de funcionar](#6-que-hacer-si-la-api-deja-de-funcionar)
7. [Re-derivar mappings desde el HTML](#7-re-derivar-mappings-desde-el-html)
8. [Plan B — providers alternativos](#8-plan-b--providers-alternativos)
9. [Aviso legal](#9-aviso-legal)

---

## 1. ⚠️ Warnings criticos

### 🚨 Warning #1 — API NO oficial, puede cambiar SIN AVISO

El endpoint `batchexecute` con los RPC IDs documentados aqui es **interno**
de Google. Google puede:

- **Renombrar RPC IDs** (`gCvqoe` → `xYZ123`) en cualquier deploy.
- **Cambiar el orden de los campos** dentro de los arrays anidados (los
  layouts posicionales documentados en `chunk_layouts.json`).
- **Cambiar el path del endpoint** (`/finance/beta/_/FinHubUi/data/batchexecute`
  → otro path).
- **Agregar requirements de auth** (cookies, headers, captcha).
- **Cerrar el endpoint completamente** y obligar a usar la API REST de
  pago.

**Frecuencia historica:** los RPC IDs de Google Finance son relativamente
estables (varios años sin grandes cambios). Pero **NO hay garantia**.

**Mitigacion:**
- Cachear los responses agresivamente (TTL 5-15 min para quote, 1 dia
  para financials).
- Tener tests de regresion que validen el formato cada deploy.
- Tener un plan-B listo (ver seccion 8).

### 🚨 Warning #2 — Layouts SIN keys

Los responses son **arrays anidados posicionales** SIN claves explicitas.
Si Google reordena campos, tu codigo va a leer mal sin error visible.

Ejemplo:
```python
# Hoy esto funciona:
price = data[0][0][5][0]
# Si Google cambia el orden, mañana data[0][0][5] puede ser otro array
# y vas a leer un timezone como si fuera precio.
```

**Mitigacion:**
- Defensive programming: validar `isinstance()` y rangos esperados antes de usar.
- Para campos criticos (precio, market cap), comparar con otra fuente
  periodicamente.

### 🚨 Warning #3 — Rate limiting y bloqueo IP

El WAF de Google es **MUY agresivo** comparado con TradingView/Yahoo.
Patrones que pueden disparar bloqueo:

- > 5 requests/segundo desde la misma IP.
- Headers incompletos (sin User-Agent valido o sin Origin).
- Requests sin cookies cuando se esperaban.
- Patrones automatizados detectables (intervalo constante).

**Sintomas de bloqueo:**
- HTTP 429 (Too Many Requests).
- HTTP 403 + redirect a captcha.
- HTTP 200 con HTML del consent screen aunque ya pasaste cookies.

**Mitigacion:**
- **Sleep ≥ 0.5s entre requests** (el modo `all` del script lo hace automaticamente).
- **Rotar User-Agent** entre requests si haces batch grandes.
- **NO usar desde CI** sin tomar precauciones (las IPs de cloud providers
  estan en blacklists frecuentes).
- Si te bloquean, esperar ~1 hora antes de reintentar.

### 🚨 Warning #4 — Sin warranty de continuidad

A diferencia de TradingView (que monetiza con paid REST API y permite
uso publico moderado), Google Finance **no monetiza directamente** este
endpoint. No hay incentivo para Google de mantenerlo estable.

Si construyes algo **importante** sobre este skill, **NO depender 100%**
de el. Tener fallback a Yahoo Finance, Finnhub, o Alpha Vantage.

---

## 2. Limitaciones tecnicas

### Sin documentacion oficial

Todo lo documentado aca fue derivado empiricamente. Hay **2 RPCs
desconocidos** (`RiQiSd` y `X12h2b`) que no pude reverse-engineer
porque sus args no son obvios.

### Sin Symbol Search expuesto

Google Finance tiene un buscador (el campo en la barra superior), pero
ese RPC NO esta entre los que se cargan en la pagina de un simbolo.
Para resolver un ticker desconocido, **usar Symbol Search de TradingView**
(skill `tradingview` → `search QUERY`).

### Sin screener / filtros

Google Finance NO tiene la funcionalidad de "buscar stocks por filtros"
expuesta via batchexecute. Para screener masivo, **usar TradingView
Scanner** (skill `tradingview` → `screen`).

### Layouts posicionales fragiles

Los arrays vienen sin keys (es el cost del wrb.fr para minimizar bytes).
Documentamos los layouts en `chunk_layouts.json` pero pueden cambiar.

### Sin WebSocket / streaming

No hay endpoint publico de streaming. Para real-time tick-by-tick,
necesitarias un broker (Alpaca, IBKR).

---

## 3. Limitaciones de cobertura

### Mercados que funcionan ✅

Verificado al 2026-06:

| Mercado | Formato ticker | Ejemplo |
|---------|----------------|---------|
| US NASDAQ | `TKR:NASDAQ` | `GGAL:NASDAQ`, `AAPL:NASDAQ` |
| US NYSE | `TKR:NYSE` | `JPM:NYSE`, `BBAR:NYSE` |
| Argentina BCBA | `TKR:BCBA` | `GGAL:BCBA`, `YPFD:BCBA` |
| Brazil B3 | `TKR:BMFBOVESPA` | `PETR4:BMFBOVESPA` |
| Spain BME | `TKR:BME` | `SAN:BME`, `TEF:BME` |
| Germany XETR | `TKR:XETR` | `SAP:XETR` |
| UK LSE | `TKR:LSE` | `HSBA:LSE` |
| Indices US | `IDX:INDEXSP/DJX/NASDAQ` | `.INX:INDEXSP`, `.DJI:INDEXDJX` |

### Mercados que NO funcionan claramente ❌

| Mercado | Razon |
|---------|-------|
| Crypto | Google Finance tiene una vista de crypto pero los RPCs documentados aqui no la cubren. Usar TradingView/Binance. |
| Bonos individuales | Los RPCs no los reconocen como simbolos validos. Usar TradingView (TVC:US10Y, etc.). |
| Forex pairs | No testeado exhaustivamente. Para forex usar OANDA / Alpha Vantage. |
| Mutual funds | Google Finance los tiene pero el formato del ticker puede ser distinto. |

### Tickers con caracteres especiales

Algunos tickers tienen `.` (`BRK.A`), `-` (`RDS-A`), `*` (`OXY*`). El
parser puede tener problemas. **Mitigacion:** URL-encode el simbolo si
da error 400.

---

## 4. Limitaciones de los datos

### Precios delayed ~15 min

Igual que TradingView/Yahoo. El timestamp del ultimo trade esta en el
campo `[11]` del quote_array — verificar contra `time.time()` para
saber el lag exacto.

### OHLC historico limitado

Variantes disponibles:
- 1-min: solo del dia actual de mercado.
- 5-min: solo del dia actual de mercado.
- daily: ultimo mes (~22 dias habiles).
- daily-6m: ~130 dias habiles.

**No hay 1+ años de daily / weekly / monthly disponibles via este
endpoint.** Para historico largo:
- US stocks: Yahoo Finance (skill `yahoo-finance`).
- Global: Alpha Vantage (requiere API key).
- Argentinos: Data912 (skill `data912`).

### OHLC 1-min NO tiene open/high/low por bar

El response del `intraday-1min` solo trae `[close, change, change_pct]`
por bar — NO open/high/low. Para OHLC real-time **usar `intraday-5min`**
que si trae los 4 campos.

### Financials muy crudos

El response de `Pr8h2e` es un array de ~40 campos sin keys. **Mapear**
las posiciones a nombres de campos requiere reverse engineering manual
y puede variar segun el tipo de empresa (banco vs tech vs energy).

Para financials estructurados con keys, usar:
- **SEC EDGAR** (skill `sec-data`) para US.
- **Macrotrends** (skill `macrotrends`) para historico global.
- **SimplyWallSt** (skill `simplywallst`).

### Currency mixta

Los financials de empresas no-US vienen en moneda nativa (ARS para GGAL).
Si necesitas USD, **convertir cliente-side** con el FX del dia.

### News bias hacia US

El feed de news de Google esta sesgado a fuentes de habla inglesa.
Para news en español/portugues sobre stocks LatAm, usar:
- **MarketScreener** (skill `marketscreener`).
- **EarningsWhispers** (skill `earningswhispers`) para transcripts.

---

## 5. Problemas conocidos por modo

### `quote` retorna `null` o `data: []`

**Causas:**
1. Ticker invalido (typo).
2. Formato invertido: pasaste `NASDAQ:GGAL` cuando es `GGAL:NASDAQ`.
3. El simbolo no existe en Google Finance (Google tiene su propio
   catalogo, no todos los tickers de TradingView estan aqui).

**Debug:**
```bash
py scripts/fetch_gfinance.py quote GGAL:NASDAQ -q
# Si retorna null, probar swapped:
py scripts/fetch_gfinance.py quote NASDAQ:GGAL -q
```

### `intraday-1min` / `intraday-5min` retornan poca data

Solo devuelven el dia actual de mercado. En fin de semana / feriado
retornan el ultimo dia habil pero con todos los bars del dia (no
parciales).

### `financials` retorna campos en posiciones distintas

El layout del `Pr8h2e` cambia segun el tipo de empresa (banco vs no-banco
tiene diferentes "line items"). El `chunk_layouts.json` documenta el
caso comun pero pueden haber variaciones.

### `news` retorna pocos items (1-5)

Para stocks no-US o de baja cobertura mediatica, Google Finance
typically tiene 1-10 noticias. Para mas, usar TradingView News o
Yahoo Finance.

### `news-related` retorna lo mismo que `news`

A veces los args `[2, 12, ...]` y `[5, 12, ...]` retornan resultados
muy similares. Si te pasa, probablemente para ese simbolo no hay
suficientes news globales relacionadas.

### `technicals` (`gXxkFd`) — interpretacion incierta

Los nombres de campos son INFERIDOS:
```
[..., bull_score, bear_score, neutral_score, rsi_value, ..., volume_score]
```

Pero Google no documenta que indicadores incluye en cada score. Si
necesitas ratings tecnicos confiables, **usar TradingView** (skill
`tradingview` → `technicals` con `Recommend.All`).

### `peers` puede no incluir los peers obvios

Google calcula peers algorithmically y a veces falla. Para GGAL puede
no incluir BBAR aunque ambos son bancos argentinos. **Validar con otra
fuente** (TradingView Scanner por industry, por ejemplo).

---

## 6. Que hacer si la API deja de funcionar

### Paso 1 — Verificar el path

Si TODOS los modos fallan con 404:

```bash
# Verificar que la URL base funciona:
curl -I https://www.google.com/finance/beta/quote/GGAL:NASDAQ
# Debe retornar 200
```

Si retorna 404, Google cambio el path. Reinspeccionar el HTML para
encontrar el nuevo path (ver seccion 7).

### Paso 2 — Verificar las cookies

Si retorna 200 pero el body es HTML del consent screen:

```python
import requests
r = requests.get("https://www.google.com/finance/quote/GGAL:NASDAQ",
                 cookies={"CONSENT": "PENDING+999",
                          "SOCS": "CAESHAgBEhJnd3NfMjAyNTAxMjMtMF9SQzMaAmVuIAEaBgiAvLW8Bg"})
print(r.url)
# Si redirige a consent.google.com, las cookies estan rotas.
```

**Capturar cookies frescas:**
1. Abrir https://www.google.com/finance/quote/GGAL:NASDAQ en un browser real.
2. Aceptar el consent screen.
3. Abrir DevTools → Application → Cookies → `.google.com`.
4. Copiar los valores de `CONSENT` y `SOCS`.
5. Guardar en `assets/consent_cookies.json`.

### Paso 3 — Verificar los RPC IDs

Si UN modo especifico falla con HTTP 400 o response vacio:

```bash
# Fetch el HTML de la pagina del simbolo:
curl 'https://www.google.com/finance/beta/quote/GGAL:NASDAQ' > /tmp/page.html

# Buscar el mapping ds:N -> rpcId:
grep -oE "'ds:[0-9]+'\\s*:\\s*\\{id:\\s*'[a-zA-Z0-9]+'" /tmp/page.html
```

Si el RPC ID que usabas no aparece, **fue renombrado**. Buscar uno
con args templates similares.

### Paso 4 — Verificar el formato del response

Si el response viene OK pero el parser falla:

```python
import requests
r = requests.post(URL, ...)
print(r.text[:2000])
# Buscar el patron )]}'\n\n<size>\n[...
# Si cambia, ajustar parse_wrbfr()
```

---

## 7. Re-derivar mappings desde el HTML

Si necesitas regenerar el mapping `RPC_ID → args templates` (porque
Google cambio los IDs), seguir este procedimiento:

### Step 1 — Fetch HTML de la pagina del simbolo

```python
import requests
COOKIES = {"CONSENT": "PENDING+999", "SOCS": "CAESHAgBEhJnd3NfMjAyNTAxMjMtMF9SQzMaAmVuIAEaBgiAvLW8Bg"}
r = requests.get("https://www.google.com/finance/beta/quote/GGAL:NASDAQ",
                 cookies=COOKIES, headers={"User-Agent": "Mozilla/5.0"})
html = r.text
```

### Step 2 — Extraer mapping ds:N -> RPC_ID + request

```python
import re

# Pattern para encontrar: 'ds:N' : {id:'XXXXX', request:[...]}
pattern = r"'(ds:\d+)'\s*:\s*\{\s*id\s*:\s*'([a-zA-Z0-9]+)'.*?request\s*:\s*(\[.+?\])(?=\s*[,}])"

for m in re.finditer(pattern, html, re.DOTALL):
    ds_key, rpc_id, request_args = m.groups()
    print(f"{ds_key} → {rpc_id}: {request_args[:150]}")
```

### Step 3 — Extraer AF_initDataCallback chunks (la data SSR)

```python
pattern = r'AF_initDataCallback\(\{key:\s*[\'"]([^\'"]+)[\'"],\s*hash:\s*[\'"]([^\'"]+)[\'"]\s*,\s*data:\s*(.+?)\s*,\s*sideChannel'

for m in re.finditer(pattern, html, re.DOTALL):
    ds_key, hash_v, data_str = m.groups()
    # data_str es JSON parseable
```

### Step 4 — Actualizar assets/rpc_ids.json

Updatear los `args_template` con los nuevos descubiertos.

---

## 8. Plan B — providers alternativos

Si Google Finance se vuelve inutilizable, **migrar a alternativas** ya
disponibles en el repo:

| Funcion | Plan B en repo | Notas |
|---------|----------------|-------|
| Quote real-time | `tradingview` (Scanner) | Mismo delay, mas robusto |
| Quote stocks AR | `data912` (real-time AR) | Real-time argentinos sin delay |
| Quote BCBA | `byma` (panels) | Local oficial |
| OHLC intraday | `alpaca-data` (1-min IEX feed) | Free tier generoso |
| OHLC daily historico | `yahoo-finance` | Mejor cobertura historica |
| Financials structured | `sec-data` (US) / `macrotrends` (global) | Con keys, no posicional |
| Analyst recommendations | `tradingview` (targets mode) / `finnhub` | Mas completo |
| Earnings | `earningswhispers` (transcripts) / `tradingview` (earnings mode) | EarningsWhispers tiene full transcripts |
| News | `tradingview` (news) / `yahoo-finance` | Mejor coverage stocks chicos |
| Indices globales | `cboe-data` (indices CBOE) / `tradingview` (Scanner) | CBOE tiene VIX y similares |
| Sectors heatmap | `tradingview` (Scanner con filter sector) | Custom queries |
| Peers / related | `tradingview` (Scanner por industry) | Mas customizable |
| Descripcion empresa | `simplywallst` / `marketscreener` | Mejor traducciones |
| Ratings tecnicos | `tradingview` (technicals con `Recommend.All`) | Mejor metodologia documentada |

### Migration helper

Si construiste algo sobre el skill `google-finance` y necesitas migrar:

```python
# Antes (con google-finance):
from fetch_gfinance import quote
q = quote("GGAL:NASDAQ")

# Despues (con tradingview):
from fetch_tradingview import quote as tv_quote
q = tv_quote("NASDAQ:GGAL")  # NOTA: invertido el orden
```

---

## 9. Aviso legal

### Uso permitido

- **Educacional / research** personal.
- **Prototipos** con bajo volumen.
- **Backtest** con cache local.

### Uso NO permitido (sin licencia)

- **Redistribuir** los datos como si fueran propios.
- **Servicio publico** que sirva datos de Google a usuarios.
- **Trading en produccion** que dependa criticamente del feed.
- **Volumen alto** (>10k requests/dia).

### Para uso comercial

Google ofrece **Google Finance via Google Sheets** (limitado pero
oficial) y la **Google Cloud Marketplace** tiene varios providers de
market data (Refinitiv, Polygon, etc) integrables con permisos
empresariales.

### Compliance

- Respetar `robots.txt` de google.com.
- No bypassear medidas de anti-abuse (captcha, IP throttling).
- Si Google detecta abuso, **puede bloquear tu IP a perpetuidad**.
- Este skill es **defensivo** — no incluye herramientas de evasion
  (rotating proxies, captcha solvers).

---

## TL;DR — checklist antes de production

- [ ] He leido los 4 warnings criticos arriba.
- [ ] Tengo cache de responses (TTL razonable).
- [ ] Tengo retry con backoff exponencial.
- [ ] Tengo sleep ≥ 0.5s entre requests.
- [ ] Tengo plan B con otro provider del repo (ver seccion 8).
- [ ] No estoy haciendo > 1k requests/dia.
- [ ] No estoy redistribuyendo los datos como propios.
- [ ] No estoy usando este skill como single source of truth para
      decisiones de trading reales.

Si marcaste todos, podes usar el skill con confianza moderada. Si fallaste
en cualquiera, **revisar antes de deployar**.
