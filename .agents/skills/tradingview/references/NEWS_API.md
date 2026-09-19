# News API — Referencia Detallada

> Endpoint: `GET https://news-headlines.tradingview.com/v2/headlines`
>
> Hasta 200 noticias recientes por request. Sin auth. **Solo `/v2/`** funciona
> — `/v3/` retorna 405 y `/v1/` retorna 404.

---

## Indice

1. [Endpoint y parametros](#1-endpoint-y-parametros)
2. [Schema del response](#2-schema-del-response)
3. [Campos detallados](#3-campos-detallados)
4. [Story detail (cuerpo de la noticia)](#4-story-detail-cuerpo-de-la-noticia)
5. [Cobertura empirica](#5-cobertura-empirica)
6. [Providers / fuentes](#6-providers--fuentes)
7. [Workflows comunes](#7-workflows-comunes)
8. [Limitaciones](#8-limitaciones)

---

## 1. Endpoint y parametros

### URL

```
GET https://news-headlines.tradingview.com/v2/headlines
```

### Query params

| Param | Tipo | Descripcion | Default |
|-------|------|-------------|---------|
| `client` | str | Cliente del request (use `web`) | (requerido) |
| `lang` | str | Idioma (`en`, `es`) — `en` tiene MUCHA mas cobertura | (requerido) |
| `symbol` | str | (opcional) ticker `NASDAQ:AAPL`. Sin symbol = headlines globales. | — |

### Variantes que NO funcionan

| Path | Status | Nota |
|------|--------|------|
| `/v3/headlines` | 405 | Method Not Allowed |
| `/headlines` | 404 | |
| `/v3/stream` | 404 | |
| `/v2/headlines/marketdata` | 404 | |
| `/v2/categories` | 404 | |
| `/v2/sections` | 404 | |
| `/v2/news` | 404 | |

### Variantes de payload que NO afectan el count

Pasar `category`, `section`, `from`, etc. en query params es ignorado o
filtra a 0. El endpoint **no soporta pagination** — siempre devuelve los
mas recientes (hasta 200).

---

## 2. Schema del response

```json
{
  "items": [
    {
      "id": "DJN_DN20260604009289:0",
      "title": "Apple's Plan for AI Dominance Rests on Fixing Its Much-Maligned Chatbot — WSJ",
      "provider": "dow-jones",
      "sourceLogoId": "dow-jones",
      "published": 1780619400,
      "source": "Dow Jones Newswires",
      "urgency": 2,
      "permission": "provider",
      "link": "https://...",
      "relatedSymbols": [
        {"symbol": "NASDAQ:AAPL", "logoid": "apple"}
      ],
      "storyPath": "/news/DJN_DN20260604009289:0/"
    }
  ]
}
```

> El response NO tiene `totalCount`. Solo `items[]`.

---

## 3. Campos detallados

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | str | ID unico de la noticia. Formato `{PROVIDER}_{INTERNALID}:0`. |
| `title` | str | Titulo de la noticia. |
| `provider` | str | Provider/agencia (`dow-jones`, `reuters`, `marketbeat`, etc.) |
| `sourceLogoId` | str | ID del logo del source (mismo que provider en general) |
| `published` | int | Timestamp unix UTC en segundos |
| `source` | str | Nombre humano del source (`Dow Jones Newswires`, `Reuters`, etc.) |
| `urgency` | int | 1 (alta) - 5 (baja). 2-3 es lo tipico. |
| `permission` | str | `provider` (publica), `pro` (requiere subscription) |
| `link` | str | URL externa al articulo original (opcional, puede faltar) |
| `relatedSymbols` | list | Lista de simbolos relacionados con `symbol` y `logoid` |
| `storyPath` | str | Path para fetch del body (ver seccion 4) |

### Conversion de `published` a fecha

```python
from datetime import datetime, timezone
dt = datetime.fromtimestamp(item["published"], tz=timezone.utc)
print(dt.isoformat())  # 2026-06-04T13:50:00+00:00
```

---

## 4. Story detail (cuerpo de la noticia)

El endpoint API directo:

```
GET /v2/story?id={story_id}
```

retorna **HTTP 400** ("Bad Request"). El cuerpo de la noticia NO esta
expuesto via JSON.

### Workaround: scrapear el HTML

```
GET https://es.tradingview.com{storyPath}
```

Devuelve **HTTP 200** con HTML ~190 KB que contiene el body de la noticia
renderizado.

El script tiene un parser best-effort en `news_story(story_path)`:

```python
{
  "url": "https://es.tradingview.com/news/...",
  "title": "Apple's Plan for AI Dominance...",
  "body": "Apple Inc. is racing to fix its Siri assistant...",
  "html_size": 191997
}
```

### Patron de extraccion

```python
import re
title_m = re.search(r'<title>([^<]+)</title>', html)
body_m = re.search(r'<article[^>]*>(.+?)</article>', html, re.DOTALL)
```

El `<article>` contiene el cuerpo principal. Limpiar tags HTML con:

```python
body_text = re.sub(r'<[^>]+>', ' ', body_m.group(1))
body_text = re.sub(r'\s+', ' ', body_text).strip()
```

---

## 5. Cobertura empirica

Coverage observada al 2026-06 con `lang=en`:

| Symbol | Items |
|--------|-------|
| `NASDAQ:AAPL` | 200 |
| `NASDAQ:MSFT` | 200 |
| `NASDAQ:NVDA` | 200 |
| `NYSE:JPM` | 200 |
| `NASDAQ:GGAL` | 1 |
| (sin symbol) | 200 (globales) |

### Por idioma

| Lang | Coverage |
|------|----------|
| `en` | 200 items para stocks grandes US |
| `es` | 0-10 items (muy escaso, casi solo MarketBeat) |
| `de`, `fr`, `pt`, etc. | Sin testear pero probablemente bajo |

**Recomendacion:** SIEMPRE usar `lang=en`. Si el caller necesita salida
en español, traducir cliente-side.

---

## 6. Providers / fuentes

Lista observada de providers:

| Provider ID | Nombre | Tipo |
|-------------|--------|------|
| `dow-jones` | Dow Jones Newswires | Profesional (premium) |
| `reuters` | Reuters | Profesional |
| `mt-newswires` | MT Newswires | Profesional |
| `tradingview-research` | TradingView Research | Editorial TV |
| `marketbeat` | MarketBeat | Retail / blog |
| `benzinga` | Benzinga | Retail / blog |
| `binance_news` | Binance News | Crypto |
| `cnbc` | CNBC | Profesional |
| `bloomberg` | Bloomberg | (paywall) |
| `seekingalpha` | Seeking Alpha | Retail editorial |
| `cointelegraph` | Cointelegraph | Crypto |
| `forexlive` | ForexLive | Forex |
| `economist` | The Economist | Editorial |

### `permission` field

| Valor | Significado |
|-------|-------------|
| `provider` | Publica, link externo accesible |
| `pro` | Requiere subscription TradingView Pro (link interno) |

---

## 7. Workflows comunes

### 1. Headlines top 10 de un symbol

```python
data = news_by_symbol("NASDAQ:AAPL", lang="en")
top_10 = data["items"][:10]
for item in top_10:
    print(f"[{item['source']}] {item['title']}")
```

### 2. Headlines filtradas por provider

```python
data = news_by_symbol("NASDAQ:AAPL", lang="en")
dj_only = [it for it in data["items"] if it["provider"] == "dow-jones"]
```

### 3. Detalle de noticia con body

```python
items = news_by_symbol("NASDAQ:AAPL")["items"]
first = items[0]
detail = news_story(first["storyPath"])
print(detail["title"])
print(detail["body"][:500])
```

### 4. Multi-symbol news aggregator

```python
symbols = ["NASDAQ:AAPL", "NASDAQ:MSFT", "NYSE:JPM"]
all_items = []
for s in symbols:
    items = news_by_symbol(s)["items"]
    all_items.extend(items)
# Dedupe por id
seen = set()
unique = []
for it in all_items:
    if it["id"] not in seen:
        seen.add(it["id"])
        unique.append(it)
# Sort por published desc
unique.sort(key=lambda x: x["published"], reverse=True)
```

### 5. Headlines globales (sin filtro)

```python
data = news_global(lang="en")
# 200 items mas recientes del mundo
```

### 6. Filtrado por urgencia

```python
data = news_by_symbol("NASDAQ:AAPL")
urgent = [it for it in data["items"] if it["urgency"] <= 2]
```

### 7. Filtrado por fecha

```python
from datetime import datetime, timezone, timedelta
data = news_by_symbol("NASDAQ:AAPL")
cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=7)).timestamp()
last_week = [it for it in data["items"] if it["published"] >= cutoff]
```

### 8. Symbols relacionados a una noticia

```python
items = news_global()["items"]
for it in items[:20]:
    syms = [s["symbol"] for s in it.get("relatedSymbols", [])]
    print(f"{it['title'][:50]} -> {syms[:3]}")
```

---

## 8. Limitaciones

1. **Sin pagination**: maximo 200 items por request, sin offset/cursor.
   Para historico mas largo, usar otros sources (no expone TradingView).

2. **Sin filtros server-side**: no se puede filtrar por provider, fecha,
   categoria. Hacer filtros cliente-side post-fetch.

3. **Coverage `lang=es`**: muy pobre. Usar `lang=en` por defecto.

4. **Body no expuesto via JSON**: requiere scrape HTML del storyPath.

5. **Sin search**: no se puede buscar por keywords en titulos. Filtrar
   cliente-side con regex sobre los 200 items.

6. **`permission: pro` items**: link interno a TradingView; sin Pro,
   solo se ve el titulo, no el contenido.

7. **Rate limiting**: tolera ~3 req/s, no documentado.

8. **News para stocks chicos**: 1-5 items, mayormente provider `marketbeat`
   o `benzinga`. Para coverage seria de stocks chicos usar Yahoo Finance
   skill complementariamente.

---

## Apendice: comparacion con otros providers de news

| Source | Coverage stocks chicos | Body via API | Pagination | Auth |
|--------|------------------------|--------------|------------|------|
| **TradingView** | ⚠️ pobre (1-5 items) | ❌ (HTML scrape) | ❌ | ❌ NO |
| Yahoo Finance | ✅ rica | ✅ JSON | ✅ | ❌ NO |
| Finnhub | ✅ rica | ✅ JSON | ✅ | ⚠️ API key |
| Alpha Vantage | ⚠️ media | ✅ JSON | ✅ | ⚠️ API key |
| Marketwatch | ✅ rica | ✅ scrape | ❌ | ❌ NO |

**Cuando usar TradingView News:**
- Stocks grandes US (AAPL/MSFT/NVDA/etc): cobertura comparable a otros.
- Noticias "premium" via Dow Jones / Reuters (que en otros lugares son paywall).
- Crypto via Binance News (no expuesto en otros skills).

**Cuando NO usar TradingView News:**
- Stocks pequeñas o no-US: usar Yahoo Finance o Finnhub.
- Historico largo: ningun endpoint publico lo expone.
- Body de noticia structured: solo TradingView Pro o el provider original.
