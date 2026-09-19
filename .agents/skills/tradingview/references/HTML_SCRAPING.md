# HTML Scraping — Extraccion de prs.init-data+json

> Las paginas de simbolo de TradingView (`es.tradingview.com/symbols/{EX}-{SYM}/{path}/`)
> son **server-side rendered**: contienen toda la data del Server en bloques
> `<script type="application/prs.init-data+json">` que se hidratan en el
> cliente. Esos bloques son **scrapeable sin ejecutar JS**, y exponen mucha
> info que NO esta en las APIs JSON.

---

## Indice

1. [Por que scrapear el HTML](#1-por-que-scrapear-el-html)
2. [Subpages confirmadas](#2-subpages-confirmadas)
3. [Estructura de prs.init-data+json](#3-estructura-de-prsinit-datajson)
4. [Bloques observados en una pagina tipica](#4-bloques-observados-en-una-pagina-tipica)
5. [Patron de extraccion](#5-patron-de-extraccion)
6. [Otros datos scrapeable del HTML](#6-otros-datos-scrapeable-del-html)
7. [Caveats](#7-caveats)

---

## 1. Por que scrapear el HTML

El Scanner API ya expone ~300+ columnas estructuradas — para la mayoria
de casos NO necesitas scrapear el HTML. Pero hay info que SOLO esta en el
HTML:

| Que solo esta en HTML | Donde |
|-----------------------|-------|
| **Tabs/subpages disponibles** para un simbolo | `<a href="/symbols/{EX}-{SYM}/{tab}/">` |
| **Breadcrumbs** (industry > sector > country) | `data.breadcrumbs[]` |
| **Similar assets** sugeridos por TV | `data.similar_assets` |
| **Featured broker** del simbolo | `data.symbol_featured_broker` |
| **Initial quotes** con full metadata | `initialQuotes` dict |
| **FAQ data** auto-generado | `symbolFaqData` |
| **Logos** (multiple sizes) | `medium_logo_urls`, `logo_id`, `base_currency_logo_id` |
| **Pricescale** (tick size) | `pricescale` |
| **Cuerpo de noticias** | `<article>` en `/news/{id}/` |

---

## 2. Subpages confirmadas

URL pattern: `https://es.tradingview.com/symbols/{EXCHANGE}-{TICKER}/{subpath}/`

Cambiar `:` por `-` en el simbolo. Ejemplo: `NASDAQ:GGAL` → `NASDAQ-GGAL`.

| Subpath | Tamaño | Que tiene en HTML |
|---------|--------|-------------------|
| `` (base) | 400 KB | Quote + chart + overview + sidebar de similar/broker |
| `technicals` | 211 KB | Ratings tabla + indicadores con BUY/SELL |
| `financials-overview` | 217 KB | Resumen financiero (income/balance) |
| `financials-income-statement` | **610 KB** | Income statement con varios periodos |
| `financials-balance-sheet` | 386 KB | Balance sheet multi-periodo |
| `financials-cash-flow` | 333 KB | Cash flow multi-periodo |
| `financials-statistics-and-ratios` | **1 MB** | Statistics + ratios completos |
| `financials-dividends` | 203 KB | Historico de dividendos |
| `financials-revenue` | 205 KB | Revenue breakdown por segmento |
| `financials-earnings` | 215 KB | Earnings history + forecast |
| `forecast` | 200 KB | Price targets + analyst forecasts |
| `ideas` | 438 KB | Ideas comunidad (autores, likes) |
| `options-chain` | 398 KB | Cadena de opciones con strikes |
| `seasonals` | 194 KB | Estacionalidad mensual |
| `bonds` | 218 KB | Bonos relacionados del mismo emisor |
| `etfs` | 256 KB | ETFs que contienen el ticker |
| `minds` | 278 KB | Comentarios cortos comunidad |

### Subpages que retornan 404

`/news/`, `/analysis/`, `/profile/`, `/markets/`, `/insider-trading/`,
`/financials-statements-and-ratios/`, `/financials-statistics/`.

---

## 3. Estructura de prs.init-data+json

Cada pagina contiene **~7 bloques** con este formato:

```html
<script type="application/prs.init-data+json">
{
  "<random_key>": {
    "context": {...},
    "data": {...},
    "meta": {...}
  }
}
</script>
```

Las **random_keys** (`wEzKaD`, `UBqnNC`, `dIwTxt`, etc.) cambian por
deploy de TradingView. NO codear contra ellas directamente — iterar.

### Tipos de bloques observados

| # | Tipo | Tamaño | Contenido |
|---|------|--------|-----------|
| 1 | `{mainMenuCategories: [...]}` | 45 KB | Menu top de TradingView (no util) |
| 2 | `{<key>: {context, data, meta}}` con `data.symbol` | 7 KB | **Datos del simbolo** ⭐ |
| 3 | `{<key>: {context, data, meta}}` mas grande | 43 KB | **Datos del subpage** ⭐ |
| 4 | `{<key>: {initialQuotes, description, symbolFaqData}}` | 1 KB | **Quote inicial** ⭐ |
| 5 | `{<key>: {languageName, blogBaseUrl, ...}}` | 130 B | Config UI |
| 6 | `{gaId, gaVars, gadwId, ...}` | 185 B | Analytics IDs |
| 7 | `{days_to_deactivation, ...}` | 189 B | User context |

Los bloques 2, 3, 4 son los **golden** — contienen la data scraping-worth.

---

## 4. Bloques observados en una pagina tipica

### Bloque del simbolo (data.symbol)

```json
{
  "wEzKaD": {
    "context": {
      "request_context": {...},
      "device": {...}
    },
    "data": {
      "symbol": {
        "pro_symbol": "NASDAQ:GGAL",
        "short_name": "GGAL",
        "instrument_name": "Grupo Financiero Galicia SA Sponsored ADR Class B",
        "exchange": "NASDAQ",
        "type": "dr",
        "country": "Argentina",
        "currency": "USD",
        "logoid": "gpo-fin-galicia",
        "pricescale": 100,
        ...
      },
      "breadcrumbs": [
        {"id": "markets", "name": "Mercados"},
        {"id": "stocks-usa", "name": "Acciones USA"},
        {"id": "sector-finance", "name": "Finance"},
        {"id": "industry-regional-banks", "name": "Regional Banks"},
        ...
      ],
      "similar_assets": {
        "items": [...]  // tickers similares sugeridos
      },
      "tabs": [...],   // pestañas disponibles
      "symbol_featured_broker": null
    },
    "meta": {...}
  }
}
```

### Bloque de initialQuotes

```json
{
  "UBqnNC": {
    "initialQuotes": {
      "pro_symbol": "NASDAQ:GGAL",
      "short_name": "GGAL",
      "exchange": "NASDAQ",
      "type": "dr",
      "typespecs": [],
      "tv_symbol_page_url_force_exchange": true,
      "ticker_title": "Grupo Financiero Galicia...",
      "instrument_name": "Grupo Financiero Galicia SA Sponsored ADR Class B",
      "medium_logo_urls": ["..."],
      "logo": {...},
      "logo_id": "gpo-fin-galicia",
      "base_currency_logo_id": "country/AR",
      "currency_logo_id": "country/US",
      "country": "Argentina",
      "data_frequency": "EOD",  // EOD (end of day) / RT (real-time)
      "pricescale": 100
    },
    "description": {...},
    "symbolFaqData": {...}  // FAQ auto-generado
  }
}
```

### Bloque de subpage especifico

Depende del subpage. Para `/technicals/`:

```json
{
  "data": {
    "symbol": {...},
    "tabs": [...],
    // ...campos especificos del technicals tab...
  }
}
```

---

## 5. Patron de extraccion

### Regex para encontrar todos los bloques

```python
import re, json

def extract_prs_blocks(html: str) -> list[dict]:
    """Extrae todos los bloques prs.init-data+json del HTML."""
    blocks = []
    for m in re.finditer(
        r'<script[^>]*type="application/prs\.init-data\+json"[^>]*>(.+?)</script>',
        html, re.DOTALL,
    ):
        try:
            blocks.append(json.loads(m.group(1).strip()))
        except json.JSONDecodeError:
            pass
    return blocks
```

### Encontrar el bloque con data del simbolo

```python
def find_symbol_block(blocks: list[dict]) -> dict | None:
    """Encuentra el bloque que contiene data.symbol."""
    for blk in blocks:
        for key, value in blk.items():
            if isinstance(value, dict) and 'data' in value:
                data = value['data']
                if isinstance(data, dict) and 'symbol' in data:
                    return data['symbol']
    return None
```

### Encontrar el initialQuotes

```python
def find_initial_quotes(blocks: list[dict]) -> dict | None:
    """Encuentra el bloque con initialQuotes."""
    for blk in blocks:
        for key, value in blk.items():
            if isinstance(value, dict) and 'initialQuotes' in value:
                return value['initialQuotes']
    return None
```

### Encontrar tabs disponibles

```python
import re

def find_tabs(html: str, symbol_with_dash: str) -> list[str]:
    """Encuentra las subpages link-eadas desde la pagina actual."""
    pattern = rf'href="(/symbols/{re.escape(symbol_with_dash)}/[a-z-]+/?)"'
    return sorted(set(re.findall(pattern, html)))
```

### Window.* assignments

Para extraer URLs de APIs internas:

```python
def find_window_vars(html: str) -> dict:
    """Extrae window.X = "Y" assignments."""
    out = {}
    for m in re.finditer(r'window\.([A-Z][A-Z_0-9]+)\s*=\s*"([^"]+)"', html):
        out[m.group(1)] = m.group(2)
    return out
```

---

## 6. Otros datos scrapeable del HTML

### Meta tags OpenGraph

```python
def extract_og_meta(html: str) -> dict:
    """Extrae meta tags og:* y twitter:*."""
    out = {}
    for m in re.finditer(
        r'<meta\s+property="(og:[^"]+|twitter:[^"]+)"\s+content="([^"]+)"',
        html
    ):
        out[m.group(1)] = m.group(2)
    return out
```

Devuelve:
- `og:title`: titulo SEO
- `og:description`: descripcion SEO
- `og:image`: URL del logo del simbolo
- `og:url`: URL canonica (puede redirigir a otro exchange)
- `twitter:*`: variantes Twitter Card

### Composicion de cartera embebida en canvas (para ETFs)

```python
def find_pie_chart(html: str) -> list[dict] | None:
    """Algunos elementos usan <canvas data-pie-chart-items-value=...>."""
    import html as html_mod
    m = re.search(r'data-pie-chart-items-value="([^"]+)"', html)
    if m:
        return json.loads(html_mod.unescape(m.group(1)))
    return None
```

### Cuerpo de noticias (en /news/{id}/)

```python
def extract_news_body(html: str) -> str | None:
    """Extrae body de noticia."""
    m = re.search(r'<article[^>]*>(.+?)</article>', html, re.DOTALL)
    if m:
        body = re.sub(r'<[^>]+>', ' ', m.group(1))
        body = re.sub(r'\s+', ' ', body).strip()
        return body
    return None
```

---

## 7. Caveats

### 1. Encoding

El HTML viene como UTF-8 valido pero contiene **entidades HTML** (`&amp;`,
`&quot;`, `&lt;`, etc.). Si extraes JSON embebido en atributos HTML, usar
`html.unescape()`:

```python
import html
clean_json = html.unescape(extracted_attr)
data = json.loads(clean_json)
```

### 2. Random keys

Los bloques `prs.init-data+json` tienen keys randomizadas que cambian
por deploy. No hardcodear keys — siempre iterar por el array y buscar el
shape esperado (`data.symbol`, `initialQuotes`, etc.).

### 3. Build hash

Las URLs internas de assets tienen un hash de build (ej:
`/static/bundles/2026.06.04-abc123.js`). Si los necesitas, extraer con
regex del HTML.

### 4. URLs canonicas pueden redirigir

`og:url` puede apuntar a otro exchange (TradingView redirige al "principal"
basado en geolocalizacion). Ejemplo: pediste `NASDAQ:GGAL` pero `og:url`
devuelve `BCBA:GGACB` porque detecto que sos de Argentina. **Usar siempre
el ticker original** que pasaste, no `og:url`.

### 5. Rate limiting mas estricto

El WAF de las paginas HTML (CloudFlare) es mas agresivo que el de las
APIs JSON. Con > 5 req/s puede dar 429. Recomendado **1 req/seg** para
scraping HTML.

### 6. Tamaño de respuestas

Las subpages financials son grandes (300 KB - 1 MB). Si haces batch de
muchos simbolos, planificar bandwidth.

### 7. Cambios estructurales

TradingView refactoriza el HTML cada ~6 meses (cambian las classes
CSS, los wrappers, etc.). Los `prs.init-data+json` blocks han sido
estables desde 2024+, pero pueden cambiar — manten tests de regresion
si dependes mucho del scraping.

### 8. Datos duplicados vs Scanner

Casi todo lo que esta en el HTML tambien esta en el Scanner. Antes de
implementar un scraper, verificar si la data esta en una columna del
Scanner — eso es muchisimo mas rapido y robusto.

**Cuando SI vale scrapear HTML:**
- Tabs disponibles (`/technicals/` existe? `/options-chain/` existe?)
- Cuerpo de noticias (no expuesto en JSON)
- Composicion de pie charts (ETFs) embebida en `<canvas>`
- Featured broker / similar assets sugeridos
- FAQ auto-generado
- Logos en distintos tamaños

**Cuando NO vale:**
- Precios, indicadores tecnicos, financials, earnings, targets → usar Scanner.
- Search → usar Symbol Search API.
- Headlines → usar News API.

---

## Apendice: ejemplo completo de scraping

```python
import re
import json
import html as html_mod
import requests

def scrape_symbol_page(symbol: str, subpath: str = "") -> dict:
    """Scrape completo de una symbol page."""
    sym_path = symbol.replace(":", "-")
    url = f"https://es.tradingview.com/symbols/{sym_path}/{subpath.strip('/')}/" if subpath else \
          f"https://es.tradingview.com/symbols/{sym_path}/"

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    h = r.text

    # Extract prs.init-data+json blocks
    blocks = []
    for m in re.finditer(
        r'<script[^>]*type="application/prs\.init-data\+json"[^>]*>(.+?)</script>',
        h, re.DOTALL,
    ):
        try:
            blocks.append(json.loads(m.group(1).strip()))
        except json.JSONDecodeError:
            pass

    # Extract symbol data
    symbol_data = None
    initial_quotes = None
    for blk in blocks:
        for key, value in blk.items():
            if isinstance(value, dict):
                if 'data' in value and isinstance(value['data'], dict):
                    if 'symbol' in value['data']:
                        symbol_data = value['data']['symbol']
                if 'initialQuotes' in value:
                    initial_quotes = value['initialQuotes']

    # Extract OG meta
    og = {}
    for m in re.finditer(
        r'<meta\s+property="(og:[^"]+|twitter:[^"]+)"\s+content="([^"]+)"', h
    ):
        og[m.group(1)] = m.group(2)

    # Extract tabs
    tabs = sorted(set(re.findall(
        rf'href="(/symbols/{sym_path}/[a-z-]+/?)"', h
    )))

    # Extract window vars (API URLs)
    window_vars = {}
    for m in re.finditer(r'window\.([A-Z][A-Z_0-9]+)\s*=\s*"([^"]+)"', h):
        window_vars[m.group(1)] = m.group(2)

    return {
        "url": url,
        "html_size": len(h),
        "symbol_data": symbol_data,
        "initial_quotes": initial_quotes,
        "og_meta": og,
        "tabs": tabs,
        "window_vars": window_vars,
        "all_blocks_count": len(blocks),
    }


# Ejemplo
result = scrape_symbol_page("NASDAQ:GGAL", "technicals")
print(json.dumps(result, indent=2, ensure_ascii=False)[:3000])
```
