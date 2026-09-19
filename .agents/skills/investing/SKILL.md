---
name: investing
description: "Investing.com via HTML scrape: cotizaciones, historico OHLCV, fundamentals (income/balance/cashflow/ratios), dividendos, earnings, perfil de empresa. 81K+ equities, 344 commodities, 10K indices, 2.4K currencies, 10K ETFs, 4.1K cryptos. Cobertura global."
license: MIT
---

# Investing.com — Datos via HTML Scrape

Skill para extraer datos de [Investing.com](https://www.investing.com) parseando el HTML publico. Sin API key, sin autenticacion.

---

## ⚠️ Aviso Legal y Tecnico

- Investing.com **no expone API publica**. Los datos se extraen de las paginas HTML con Cloudflare bot protection.
- **Dependencia obligatoria:** `curl_cffi` (impersona Chrome 120 a nivel TLS — `requests` puro devuelve el challenge de Cloudflare, no datos).
- **Rate limit agresivo:** respetar 1-2 segundos entre requests. Cloudflare devuelve 429/403 si se hacen muchas requests muy rapido. El script reintenta con backoff automatico.
- **Datos delayed:** el precio mostrado en la pagina es el del ultimo cierre disponible (15-20 min de delay para US equities, similar para otros).
- **Respetar terminos de servicio** de Investing.com. No hacer mas de 1-2 requests/segundo. No usar para redistribuir masivamente.
- Investing.com se reserva el derecho de bloquear rangos de IP. El skill puede dejar de funcionar en cualquier momento.

---

## Scripts

| Script | Descripcion |
|--------|-------------|
| **[fetch_investing.py](./scripts/fetch_investing.py)** | Script principal: todos los modos disponibles |

---

## Instalacion de dependencias

```bash
pip install curl_cffi
```

> NO funciona con `requests` puro. Cloudflare detecta y bloquea.

---

## Uso rapido

```bash
# === COTIZACIONES (auto-detect tipo) ===
python scripts/fetch_investing.py quote gold
python scripts/fetch_investing.py quote eur-usd
python scripts/fetch_investing.py quote us-spx-500
python scripts/fetch_investing.py quote bitcoin
python scripts/fetch_investing.py quote ypf-sa --type equities
python scripts/fetch_investing.py quote apple-computer-inc -q

# === BUSQUEDA EN SITEMAPS ===
python scripts/fetch_investing.py search YPF
python scripts/fetch_investing.py search gold --category commodities
python scripts/fetch_investing.py search MERVAL --category indices
python scripts/fetch_investing.py search AR --category currencies --limit 30

# === SITEMAPS COMPLETOS ===
python scripts/fetch_investing.py sitemap commodities    # 344 instrumentos
python scripts/fetch_investing.py sitemap currencies     # 2,394 cruces
python scripts/fetch_investing.py sitemap indices        # 20K+ indices
python scripts/fetch_investing.py sitemap equities       # 81K+ acciones
python scripts/fetch_investing.py sitemap etfs           # 30K+ ETFs

# === HISTORICO OHLCV ===
python scripts/fetch_investing.py historical gold
python scripts/fetch_investing.py historical eur-usd
python scripts/fetch_investing.py historical ypf-sa --pages 5  # ~115 dias
python scripts/fetch_investing.py historical apple-computer-inc

# === FUNDAMENTALS ===
python scripts/fetch_investing.py profile apple-computer-inc
python scripts/fetch_investing.py financials apple-computer-inc --ftype income
python scripts/fetch_investing.py financials apple-computer-inc --ftype balance
python scripts/fetch_investing.py financials apple-computer-inc --ftype cashflow
python scripts/fetch_investing.py ratios apple-computer-inc
python scripts/fetch_investing.py dividends apple-computer-inc
python scripts/fetch_investing.py earnings apple-computer-inc

# === GUARDAR A ARCHIVO ===
python scripts/fetch_investing.py quote gold -o gold_quote.json
python scripts/fetch_investing.py historical ypf-sa -o ypf_hist.json

# === MODO SILENCIOSO (solo JSON, sin logs) ===
python scripts/fetch_investing.py quote gold -q
```

---

## Modos disponibles

| Modo | Data | Endpoint |
|------|------|----------|
| `quote` | Cotizacion (precio, cambio, OHLC, volume, pair_id) | `www.investing.com/{type}/{slug}` |
| `search` | Busqueda fuzzy sobre sitemaps publicos | Sitemap XMLs |
| `sitemap` | Descarga sitemap completo (URLs de instrumentos) | Sitemap XMLs |
| `historical` | Historico OHLCV desde la tabla HTML | `/{type}/{slug}-historical-data` |
| `profile` | Descripcion, sector, industria, pais, sede, empleados | `/{type}/{slug}-company-profile` |
| `financials` | Income / Balance / Cash Flow (TTM + ultimos 5 anios) | `/{type}/{slug}-income-statement` etc. |
| `ratios` | Margenes, retornos, valuation ratios | `/{type}/{slug}-ratios` |
| `dividends` | Historial completo de dividendos | `/{type}/{slug}-dividends` |
| `earnings` | Earnings history (EPS real vs estimado) | `/{type}/{slug}-earnings` |

---

## Tipos de instrumentos

| Tipo | `--type` | Slug example | Cobertura |
|------|----------|--------------|-----------|
| Equity (stock/ADR) | `equities` | `apple-computer-inc`, `ypf-sa`, `ggal` | 81,518 |
| Commodity | `commodities` | `gold`, `crude-oil`, `brent-oil` | 344 |
| Indice | `indices` | `us-spx-500`, `ibovespa`, `dax` | 20,000+ |
| Currency pair (forex) | `currencies` | `eur-usd`, `usd-ars`, `brl-usd` | 2,394 |
| ETF | `etfs` | `spdr-s-p-500`, `vanguard-ftse-all-world` | 30,000+ |
| Crypto | `crypto` | `bitcoin`, `ethereum` | 4,135+ coins, 20K+ pairs |
| Tasa / Bono | `rates-bonds` | (no en sitemap directo) | 20,000+ |
| Fondo | `funds` | (no en sitemap directo) | 100K+ |
| Certificado | `certificates` | (no en sitemap directo) | 6,222 |

> **Auto-deteccion:** si no pasas `--type`, el script prueba commodities → currencies → indices → etfs → crypto → equities. Las equities son las mas lentas/rate-limited, asi que se prueban al final.

---

## Slugs utiles (Argentina / LatAm)

| Slug | Nombre | Simbolo | Tipo |
|------|--------|---------|------|
| `ypf-sa` | YPF Sociedad Anonima | YPF | equities |
| `ypf-sociedad` | YPF Sociedad (variante) | YPF | equities |
| `pampa-energia` | Pampa Energia SA | PAMPm | equities |
| `pampa-energia-sa` | Pampa Energia ADR | PAM | equities |
| `central-puerto` | Central Puerto S.A. | CEPUm | equities |
| `central-puerto-adr` | Central Puerto ADR | CEPU | equities |
| `tenaris` | Tenaris SA | TENR | equities |
| `tenaris-sa` | Tenaris ADR | TS | equities |
| `bbva` | Banco Bilbao Vizcaya Argentaria | BBVA | equities |
| `banco-macro-sa` | Banco Macro SA | BMA | equities |
| `mercadolibre` | MercadoLibre | MELI | equities |
| `mercadolibre-inc` | MercadoLibre Inc | MELI | equities |
| `globant-sa` | Globant SA | GLOB | equities |
| `globant-cedear` | Globant CEDEAR | GLOBm | equities |
| `despegar-com` | Despegar | DESP | equities |
| `despegar-ba` | Despegar Buenos Aires | DESPm | equities |
| `galicia-b` | Grupo Financiero Galicia (BA) | GGALm | equities |
| `grupo-financiero-galicia-sa-adr` | Grupo Financiero Galicia ADR | GGAL | equities |
| `edenor` | Edenor | EDNm | equities |
| `transportadora-de-gas-del-sur-sa` | TGS SA | TGSm | equities |
| `siderar` | Ternium / Siderar | TXR | equities |
| `aluar` | Aluar | ALUA | equities |
| `mirgor` | Mirgor | MIRG | equities |
| `loma-negra` | Loma Negra | LOMA | equities |
| `cresud` | Cresud | CRESY | equities |
| `transener` | Transener | TRAN | equities |
| `capex` | Capex | CAPX | equities |
| `solvay` | Solvay | SOLB | equities |
| `holcim` | Holcim | HCMLY | equities |
| `consultatio-s.` | Consultatio | CONO | equities |
| `garovaglio` | Garovaglio | GCLA | equities |
| `laboratorios-richmond` | Laboratorios Richmond | RICH | equities |
| `longvie` | Longvie | LONG | equities |
| `rigolleau` | Rigolleau | RIGO | equities |

### Currencies (FX)

| Slug | Par | Notas |
|------|-----|-------|
| `usd-ars` | USD/ARS (oficial) | Dolar oficial |
| `eur-usd` | EUR/USD | Mayor |
| `brl-usd` | BRL/USD (oficial) | Dolar oficial Brasil |
| `mxn-usd` | MXN/USD (oficial) | Peso mexicano |
| `ars-brl` | ARS/BRL | Peso argentino vs real |
| `ars-mxn` | ARS/MXN | Peso argentino vs peso mexicano |
| `aed-ars` | AED/ARS | Dirham → Peso |

> **MEP / CCL / Blue:** Investing.com no expone estos pares derivados como tales. Para MEP/CCL/blue, usar [data912](./../data912/) que sí los cubre.

---

## Datos devueltos

### `quote`

```json
{
  "last": "4,501.47",         // precio formateado (con separadores)
  "last_raw": 4501.47,         // precio como float
  "change": -0.78,             // cambio absoluto vs last_close
  "change_pct": -0.02,         // (no siempre presente)
  "last_close": 4502.25,       // (no siempre presente)
  "bid": 4500.74,              // bid (commodities, currencies)
  "ask": 4501.19,              // ask
  "open": 4502.5,              // apertura del dia
  "high": 4508.75,             // maximo del dia
  "low": 4499.97,              // minimo del dia
  "volume": 1633,              // volumen
  "avg_volume": 0,             // volumen promedio
  "prev_close": null,          // cierre anterior
  "pair_id": 1057391,          // ID interno de investing.com
  "name": "Gold Futures",      // nombre completo
  "symbol": "GC",              // ticker
  "currency": "USD",           // moneda
  "exchange": null,            // exchange
  "country": null,             // pais
  "updated_epoch": 1749091200, // timestamp ultima actualizacion
  "page_title": "Gold Futures - Investing.com",
  "slug": "gold",
  "type": "commodities",
  "url": "https://www.investing.com/commodities/gold"
}
```

> **Nota:** no todos los campos aparecen en todos los instrumentos. Equities suelen tener `last`, `last_raw`, `change`, `bid`, `ask`, `open`, `high`, `low`, `volume`, `prev_close`, `pair_id`, `name`, `symbol`, `currency`, `exchange`. Commodities suelen incluir ademas `updated_epoch`.

### `historical`

```json
{
  "slug": "gold",
  "type": "commodities",
  "count": 23,
  "rows": [
    {
      "date": "Jun 04, 2026",
      "price": "4,497.70",
      "open": "4,481.76",
      "high": "4,543.12",
      "low": "4,470.55",
      "vol": "3.16K",
      "change_pct": "+0.69%"
    },
    ...
  ]
}
```

> 23 dias por default (1 pagina). Usar `--pages 5` para ~115 dias, etc.

### `financials`

Devuelve estructura con periodos (TTM, 2024, 2023, 2022, 2021, 2020) y filas con label + valores:

```json
{
  "slug": "apple-computer-inc",
  "type": "equities",
  "ftype": "income",
  "periods": ["TTM", "2024", "2023", "2022", "2021", "2020"],
  "count": 23,
  "rows": [
    {"label": "Total Revenue", "values": ["394,328", "385,100", "383,285", "394,328", "365,817", "274,515"]},
    {"label": "Gross Profit", "values": ["170,000", ...]},
    ...
  ]
}
```

> `--ftype income` | `balance` | `cashflow`

### `ratios`

Misma estructura que `financials` pero con ratios (margenes, retornos, valuation, etc).

### `dividends`

Array de filas con celdas (fecha, dividend, yield, etc):

```json
{
  "slug": "apple-computer-inc",
  "type": "equities",
  "count": 18,
  "rows": [
    ["Ex-Dividend Date", "May 09, 2025", "Quarterly", "0.26", "..."],
    ...
  ]
}
```

### `earnings`

Array de filas (date, EPS actual, EPS estimado, surprise, etc):

```json
{
  "slug": "apple-computer-inc",
  "type": "equities",
  "count": 20,
  "rows": [
    ["Aug 01, 2024", "Q3 2024", "1.40", "1.35", "+3.70%", "..."],
    ...
  ]
}
```

---

## Consideraciones tecnicas

### ¿Por que `curl_cffi` y no `requests`?

Investing.com usa Cloudflare con proteccion anti-bot a nivel TLS. El User-Agent no importa — Cloudflare hace **TLS fingerprinting** y rechaza clientes que no sean navegadores reales.

- `requests` (Python puro, TLS fingerprint de Python urllib3): **bloqueado**, devuelve challenge HTML.
- `curl_cffi.requests.Session(impersonate="chrome120")`: **pasa el challenge** porque impersona el fingerprint TLS de Chrome 120.

`curl_cffi` es un wrapper sobre `curl-impersonate` (fork de libcurl con fingerprints pre-cargados). Es una libreria con wheels precompilados para Windows/Mac/Linux — instalar y usar sin compilar nada.

### Rate limit y Cloudflare

Cloudflare impone rate limits agresivos:
- **/equities/** es el path mas rate-limited (mas requests, mas proteccion)
- **/commodities/**, **/currencies/**, **/indices/** son mas permisivos
- Si haces 10+ requests en pocos segundos → 429 o 403 con "Just a moment..."
- Backoff recomendado: **2-3 segundos entre requests**
- Si recibis 429, esperar 1-2 minutos

El script maneja esto con retries + backoff exponencial. Si el IP esta muy marcado, la unica solucion es esperar o usar un proxy residencial.

### Auto-deteccion de tipo

Cuando no se pasa `--type`, el script prueba los 6 paths uno por uno. Esto dispara 6 requests, lo que puede rate-limitar. **Recomendacion:** pasar `--type` siempre que se sepa.

Orden de prueba (mas rapido primero):
1. `commodities` (344 instrumentos)
2. `currencies` (2,394)
3. `indices` (20K+)
4. `etfs` (30K+)
5. `crypto` (4K+)
6. `equities` (81K+, rate-limited)

### Sitemaps

Los sitemaps son la **unica fuente totalmente publica** y no rate-limited. Son utiles para:
- Descubrir slugs de instrumentos (no hay API de "search" publica)
- Construir catalogos locales
- Backups de listings

Cantidad de instrumentos por sitemap (verificado 2026-06-04):
- equities: 81,518 (9 archivos)
- commodities: 344 (1 archivo)
- indices: 20,000+ (2 archivos)
- currencies: 2,394 (2 archivos)
- etfs: 30,000+ (3 archivos)
- crypto coins: 4,135
- crypto pairs: 20,000+ (2 archivos)
- rates/bonds: 20,000+ (2 archivos)
- funds: 100K+ (11 archivos)
- certificates: 6,222

---

## Limitaciones

1. **Rate limit agresivo:** en uso intensivo, CF puede bloquear el IP. Es problema del sitio, no del script.
2. **Cloudflare puede romper el skill en cualquier momento** cambiando el challenge.
4. **Historico paginado:** 23 dias por default, hay que pasar `--pages` para mas.

---


## Estructura del skill

```
skills/investing/
├── SKILL.md                          # Este archivo (guia rapida)
├── references/
│   └── REFERENCE.md                  # Documentacion completa + endpoints
└── scripts/
    └── fetch_investing.py            # Script principal
```

---

> **Documentacion detallada:** Consultar [references/REFERENCE.md](./references/REFERENCE.md) para la documentacion exhaustiva de los endpoints, estructuras JSON, ejemplos y troubleshooting.
