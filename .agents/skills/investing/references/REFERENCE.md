# Investing.com — Documentacion Tecnica

Documentacion completa de los endpoints, estructuras JSON, regex de extraccion y troubleshooting.

---

## Tabla de contenidos

1. [Arquitectura de extraccion](#arquitectura-de-extraccion)
2. [Sitemaps publicos](#sitemaps-publicos)
3. [Endpoints HTML](#endpoints-html)
4. [Patrones de extraccion (regex)](#patrones-de-extraccion-regex)
5. [Rate limit y Cloudflare](#rate-limit-y-cloudflare)
6. [Slugs descubiertos (Argentina / LatAm)](#slugs-descubiertos-argentina--latam)
7. [Troubleshooting](#troubleshooting)
8. [Comparacion con otras skills](#comparacion-con-otras-skills)

---

## Arquitectura de extraccion

```
┌─────────────────────────────────────────────────────────────┐
│ Script Python (curl_cffi impersonate chrome120)             │
│   ↓                                                         │
│ Cloudflare (TLS fingerprint check)                          │
│   ↓ pasa                                                    │
│ Investing.com HTML (con datos embebidos en JSON)            │
│   ↓                                                         │
│ Regex parser → JSON output                                  │
└─────────────────────────────────────────────────────────────┘
```

**Componentes clave:**

1. **HTTP client:** `curl_cffi.requests.Session(impersonate="chrome120")`
   - Impersona TLS fingerprint de Chrome 120
   - Headers minimos (User-Agent, Accept, Accept-Language)
   - Sin cookies explicitas, sin proxies

2. **Retry logic:** 3 intentos con backoff exponencial
   - `2.0s` entre requests normales
   - `+5s` despues de 429
   - `+3s` despues de 403
   - Max ~30s de espera total

3. **Parser:** regex sobre HTML
   - Precios: `data-test="instrument-price-last"`, JSON embebido `{"last":...}`
   - Historico: tabla HTML con clase `hist`
   - Sitemaps: `<loc>URL</loc>` en XML
   - Fundamentals: pares label/value en tablas HTML

---

## Sitemaps publicos

URLs de sitemaps (verificados 2026-06-04):

| Categoria | Archivos | Total URLs | Cobertura |
|-----------|----------|------------|-----------|
| **equities** | `equities_ov_sitemap.xml` + 9 archivos `_2.xml` a `_9.xml` | **81,518** | Stocks globales + ADRs |
| **commodities** | `commodities_ov_sitemap.xml` | **344** | Materias primas + futuros |
| **indices** | `indices_ov_sitemap.xml` + `_2.xml` | **20,000+** | Indices globales |
| **currencies** | `currencies_ov_sitemap.xml` + `_2.xml` | **2,394** | Pares FX |
| **etfs** | `etfs_ov_sitemap.xml` + 2 archivos | **30,000+** | ETFs globales |
| **crypto_coins** | `crypto_coins_ov_sitemap.xml` | **4,135** | Monedas crypto |
| **crypto_pairs** | `crypto_pairs_ov_sitemap.xml` + `_2.xml` | **20,000+** | Pares crypto |
| **rates_bonds** | `rates-bonds_ov_sitemap.xml` + `_2.xml` | **20,000+** | Tasas y bonos |
| **funds** | `funds_ov_sitemap.xml` + 11 archivos `_2.xml` a `_11.xml` | **100K+** | Fondos |
| **certificates** | `certificates_ov_sitemap.xml` | **6,222** | Certificados |

### Sitemap index

```bash
https://www.investing.com/sitemap_index.xml
```

Lista 53 sitemaps (incluye news, analysis, ec_events, etc.) — no todos son de instrumentos.

### Estructura del XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.investing.com/equities/boeing-co</loc>
    <lastmod>2026-06-04T17:30:00+00:00</lastmod>
    <changefreq>daily</changefreq>
  </url>
  ...
</urlset>
```

> Los sitemaps **no son rate-limited** — son el unico endpoint con acceso irrestricto. Util para construir catalogos locales.

---

## Endpoints HTML

### Estructura de URLs

```
https://www.investing.com/{type}/{slug}
https://www.investing.com/{type}/{slug}-historical-data
https://www.investing.com/{type}/{slug}-company-profile
https://www.investing.com/{type}/{slug}-income-statement
https://www.investing.com/{type}/{slug}-balance-sheet
https://www.investing.com/{type}/{slug}-cash-flow
https://www.investing.com/{type}/{slug}-ratios
https://www.investing.com/{type}/{slug}-dividends
https://www.investing.com/{type}/{slug}-earnings
```

### Endpoints disponibles por tipo

| Tipo | Path | Endpoints validados |
|------|------|---------------------|
| **equities** | `/equities/{slug}` | quote, historical, profile, income-statement, balance-sheet, cash-flow, ratios, dividends, earnings, company-profile, options |
| **commodities** | `/commodities/{slug}` | quote, historical |
| **indices** | `/indices/{slug}` | quote, historical, components |
| **currencies** | `/currencies/{slug}` | quote, historical |
| **etfs** | `/etfs/{slug}` | quote, historical, profile, holdings |
| **crypto** | `/crypto/{slug}` | quote, historical |
| **rates-bonds** | `/rates-bonds/{slug}` | quote, historical |


## Patrones de extraccion (regex)

### 1. Precio actual

**HTML data-test attribute** (mas confiable):
```regex
data-test="instrument-price-last"[^>]*>([0-9.,]+)<
```

Ejemplo HTML:
```html
<span data-test="instrument-price-last">311.23</span>
```

**JSON embebido:**
```regex
"last"\s*:\s*([\d.]+)
```

Ejemplo HTML (en script inline):
```html
<script>
  window.__NEXT_DATA__ = { "props": { ... "last": 311.23 ... } }
</script>
```

### 2. Datos de cotizacion (JSON embebido)

```regex
"last"\s*:\s*([\d.]+)              // precio
"last_close"\s*:\s*([\d.]+)        // cierre anterior
"change"\s*:\s*"?(-?[\d.]+)"?      // cambio absoluto
"change_pct"\s*:\s*"?(-?[\d.]+)"?  // cambio porcentual
"bid"\s*:\s*([\d.]+)               // bid
"ask"\s*:\s*([\d.]+)               // ask
"open"\s*:\s*([\d.]+)              // apertura
"high"\s*:\s*([\d.]+)              // maximo
"low"\s*:\s*([\d.]+)               // minimo
"volume"\s*:\s*"?(\d+)"?           // volumen
"avg_volume"\s*:\s*"?(\d+)"?       // volumen promedio
"prev_close"\s*:\s*([\d.]+)        // cierre previo
"pair_id"\s*:\s*(\d+)              // ID interno
"name"\s*:\s*"([^"]+)"\s*,\s*"symbol"\s*:\s*"([^"]+)"  // nombre + simbolo
"currency"\s*:\s*"([^"]+)"         // moneda
"exchange"\s*:\s*"([^"]+)"         // exchange
"country"\s*:\s*"([^"]+)"          // pais
"updated_time"\s*:\s*"?(\d+)"?     // timestamp actualizacion (epoch)
"timezone"\s*:\s*"([^"]+)"         // timezone
```

### 3. Historico (tabla HTML)

**Selector de filas:**
```regex
<tr[^>]+class="[^"]*hist[^"]*"[^>]*>(.+?)</tr>
```

**Selector de celdas:**
```regex
<td[^>]*>(.+?)</td>
```

**Limpieza de HTML dentro de celdas:**
```python
text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', td)).strip()
```

**Estructura de filas** (7 columnas, en orden):
1. `date` — formato "Mon DD, YYYY" (ej: "Jun 04, 2026")
2. `price` — precio de cierre (formateado con comas)
3. `open` — apertura
4. `high` — maximo
5. `low` — minimo
6. `vol` — volumen (formateado, ej: "106.69K", "1.2M")
7. `change_pct` — cambio % del dia (ej: "+0.69%")

### 4. Sitemaps (XML)

```regex
<loc>([^<]+)</loc>
```

Estructura de URL: `https://www.investing.com/{type}/{slug}`

### 5. Profile (pares label/value)

```regex
>([A-Z][A-Za-z ]{2,40})</[a-z][^>]*>\s*<[a-z][^>]*>([^<]{1,100})<
```

Captura pares como:
- `Sector` → `Technology`
- `Industry` → `Consumer Electronics`
- `Country` → `United States`
- `Employees` → `164,000`

### 6. Financials (tabla de periodos + filas)

**Headers de periodos:**
```regex
<th[^>]+scope="col"[^>]*>\s*<span[^>]*>([^<]+)</span>
```

Captura: `TTM`, `2024`, `2023`, `2022`, `2021`, `2020`

**Filas de valores:**
```regex
<td[^>]*>(.+?)</td>
```

Primera celda = label, resto = valores numericos

---

## Rate limit y Cloudflare

### Cloudflare bot protection

Investing.com usa Cloudflare con las siguientes protecciones:

1. **TLS fingerprinting** — identifica clientes que no son navegadores reales
   - Python `urllib3` (usado por `requests`): fingerprint = "Python", **bloqueado**
   - `curl_cffi` con `impersonate="chrome120"`: fingerprint = "Chrome 120", **pasa**
   - `curl-impersonate` (C library): tambien funciona

2. **JS challenge** ("Just a moment...")
   - Se muestra en respuestas 403
   - Pasa automaticamente al hacer el request con TLS fingerprint correcto

3. **Rate limit por IP** — 429 si se hacen muchas requests rapido
   - /equities/ es el mas protegido
   - /commodities/, /currencies/, /indices/ son mas permisivos
   - Backoff recomendado: 2-3 segundos entre requests

### Headers minimos

```python
{
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}
```

> User-Agent viene del `impersonate` — no hay que setearlo manualmente.

### Backoff del script

```python
sleep=2.0       # entre requests normales
+5s, +10s       # despues de 429
+3s, +5s        # despues de 403
max retries=3   # total ~30s de espera
```

Si despues de 3 retries no responde, devuelve `{"error": "no se pudo obtener ..."}`.

### ¿Por que el IP queda rate-limited?

Si haces 20+ requests en 30 segundos, Cloudflare te marca como bot. La unica forma de "desbloquear" es esperar 5-15 minutos sin hacer requests. Para uso intensivo, usar proxies residenciales o un pool de IPs.

---

## Slugs descubiertos (Argentina / LatAm)

### Argentina

Lista verificada de slugs para empresas AR comunes:

| Slug | Empresa | Ticker BA | Ticker ADR |
|------|---------|-----------|------------|
| `grupo-financiero-galicia` | Galicia | GGAL | GGAL |
| `galicia-b` | Galicia Clase B | GGALm | - |
| `grupo-financiero-galicia-sa-adr` | Galicia ADR | - | GGAL |
| `ypf-sa` | YPF (BA) | YPF | - |
| `ypf-sociedad` | YPF Sociedad (variante BA) | YPFm | - |
| `pampa-energia` | Pampa Energia (BA) | PAMPm | - |
| `pampa-energia-sa` | Pampa Energia ADR | - | PAM |
| `central-puerto` | Central Puerto (BA) | CEPUm | - |
| `central-puerto-adr` | Central Puerto ADR | - | CEPU |
| `banco-macro-sa` | Banco Macro ADR | - | BMA |
| `bbva` | BBVA (BA) | BBVA | - |
| `tenaris` | Tenaris (BA) | TENR | - |
| `tenaris-sa` | Tenaris ADR | - | TS |
| `mercadolibre` | MercadoLibre (BA) | MELI | - |
| `mercadolibre-inc` | MercadoLibre Inc | - | MELI |
| `mercadolibre-bdr` | MercadoLibre BDR | MELI | - |
| `globant-sa` | Globant | - | GLOB |
| `globant-cedear` | Globant CEDEAR | GLOBm | - |
| `despegar-com` | Despegar (BA) | DESP | - |
| `despegar-ba` | Despegar Buenos Aires | DESPm | - |
| `edenor` | Edenor (BA) | EDNm | - |
| `edenor-sa` | Edenor SA | EDN | - |
| `transportadora-de-gas-del-sur-sa` | TGS (BA) | TGSm | - |
| `siderar` | Ternium / Siderar | TXR | - |
| `aluar` | Aluar | ALUA | - |
| `mirgor` | Mirgor | MIRG | - |
| `loma-negra` | Loma Negra | LOMA | - |
| `loma-negra-ba` | Loma Negra BA | LOMAm | - |
| `cresud` | Cresud | CRESY | - |
| `transener` | Transener | TRAN | - |
| `capex` | Capex | CAPX | - |
| `solvay` | Solvay | SOLB | - |
| `solvay-adr` | Solvay ADR | - | SOLVY |
| `holcim` | Holcim | HCMLY | - |
| `consultatio-s.` | Consultatio | CONO | - |
| `garovaglio` | Garovaglio | GCLA | - |
| `laboratorios-richmond` | Laboratorios Richmond | RICH | - |
| `longvie` | Longvie | LONG | - |
| `rigolleau` | Rigolleau | RIGO | - |
| `metrogas` | Metrogas | METR | - |

### Brasil

| Slug | Empresa |
|------|---------|
| `petrobras-on` | Petrobras ON |
| `petrobras-pn` | Petrobras PN |
| `petrobras-arg` | Petrobras Argentina |
| `vale-s.a.--americ` | Vale ADR |
| `ambev-on` | Ambev ON |
| `ambev-pn` | Ambev PN |
| `weg-on-ej-nm` | WEG ON |
| `itausa-on-ej-n1` | Itausa ON |
| `bradesco-on-n1` | Bradesco ON |
| `banco-bradesco` | Bradesco |

### Mexico

| Slug | Empresa |
|------|---------|
| `cemex-cpo` | Cemex CPO |
| `cemex-a` | Cemex A |
| `cemex-sab-de-cv-adr` | Cemex ADR |
| `coca-cola-femsa-adr` | Femsa ADR |
| `grupo-televisa-sa-adr` | Televisa ADR |
| `grupo-televisa-cp` | Televisa CP |
| `walmex` | Walmart Mexico |

### Currencies AR

| Slug | Par |
|------|-----|
| `usd-ars` | USD/ARS oficial |
| `ars-usd` | ARS/USD |
| `ars-brl` | ARS/BRL |
| `ars-mxn` | ARS/MXN |
| `ars-eur` | ARS/EUR |
| `aed-ars` | AED/ARS |
| `ars-cad` | ARS/CAD |
| `brl-ars` | BRL/ARS |
| `eur-ars` | EUR/ARS |

> **MEP / CCL / Blue:** no existen como tales en investing.com. Para esos, usar [data912](../data912/).

### Indices LatAm

| Slug | Indice |
|------|--------|
| `ibovespa-usd` | Bovespa USD |
| `ibovespa-eur` | Bovespa EUR |
| `ibovespa-futures` | Bovespa Futures |
| `merval` | MERVAL (verificar slug) |
| `ipc` | IPC Mexico |
| `ftse-latibex` | FTSE Latibex |

> **Nota:** MERVAL puede haber cambiado de nombre/slug despues de la reestructuracion del indice. Buscar con `search` para encontrar el slug actual.

---

## Troubleshooting

### Error: "Just a moment..." en la respuesta

**Causa:** Cloudflare challenge. El script **no** esta pasando el TLS fingerprint.

**Solucion:**
1. Verificar que `curl_cffi` esta instalado: `pip show curl_cffi`
2. Verificar la version: `python -c "import curl_cffi; print(curl_cffi.__version__)"` (>= 0.5)
3. Probar manualmente:
   ```python
   from curl_cffi import requests
   s = requests.Session(impersonate="chrome120")
   r = s.get("https://www.investing.com/")
   print("Just a moment" in r.text)  # debe ser False
   ```
4. Si sigue fallando, probar con `impersonate="chrome124"` (version mas nueva)

### Error: 429 Rate limit

**Causa:** Demasiadas requests muy rapido.

**Solucion:**
- Esperar 1-2 minutos antes de seguir
- Aumentar el sleep entre requests (modificar `sleep` en el script)
- Usar `--type` siempre (evita autodetect que prueba 6 paths)
- Considerar usar un proxy residencial

### Error: 403 Forbidden persistente

**Causa:** IP marcada por Cloudflare. Pasa cuando se hacen 20+ requests en 30 segundos.

**Solucion:**
- Esperar 5-15 minutos sin hacer requests
- Cambiar de IP (VPN, proxy)
- Reducir frecuencia de requests

### Error: "slug 'XXX' no encontrado"

**Causa:** El slug no existe o la autodeteccion fallo.

**Solucion:**
1. Buscar el slug correcto:
   ```bash
   python fetch_investing.py search GALICIA
   python fetch_investing.py search YPF
   ```
2. Verificar el path manualmente: `https://www.investing.com/equities/{slug}`
3. Probar variantes (a veces hay ADR vs local, BA vs NY, etc.)

### Error: "no se pudo obtener /equities/..."

**Causa:** /equities/ es el path mas rate-limited. La autodeteccion prueba commodities/currencies/indices primero, pero si el slug es de equities y se pasa sin --type, puede fallar.

**Solucion:**
- Pasar `--type equities` siempre que se sepa
- Esperar y reintentar

### Historico vacio (`rows: []`)

**Causa:** El instrumento no tiene historico publico (ej: CEDEARs, certificados) o el regex fallo.

**Solucion:**
- Verificar manualmente: `https://www.investing.com/equities/{slug}-historical-data`
- Si la pagina tiene tabla con clase "hist", el script deberia extraerla
- Reportar como issue si falla en un instrumento conocido

### `last_close` o `change_pct` no aparecen

**Causa:** El JSON embebido no incluye ese campo para ese instrumento (comun en forex y algunos commodities).

**Solucion:**
- Usar `change` y `prev_close` si estan disponibles
- Calcular manualmente: `change_pct = change / prev_close * 100`

---

## Comparacion con otras skills

| Caracteristica | Investing.com | Yahoo Finance | CBOE Data | Finnhub |
|----------------|---------------|---------------|-----------|---------|
| **Cobertura global** | ✅ 81K+ equities, 30K+ ETFs | ✅ 200K+ tickers | ❌ US only | ⚠️ US/EU |
| **Tipos de instrumentos** | 10+ | 5+ | 3 (indices, options, futures) | 6+ |
| **Forex** | ✅ 2,394 cruces | ⚠️ Limitado | ❌ | ✅ |
| **Commodities** | ✅ 344 | ⚠️ Limitado | ✅ VX futures | ❌ |
| **Crypto** | ✅ 4,135 | ✅ | ❌ | ✅ |
| **Opciones** | ❌ JS dinamico | ✅ | ✅ Chains completas | ❌ |
| **Futuros** | ⚠️ Limitado | ⚠️ Limitado | ✅ VX, IBHY, IBIG | ❌ |
| **Historial largo** | ✅ 20+ anios | ✅ 50+ anios | ⚠️ Annual snapshots | ⚠️ Freemium |
| **Real-time** | ❌ Delayed 15-20min | ❌ Delayed 15min | ❌ Delayed | ✅ Con plan |
| **API key** | No | No | No | Si (free tier) |
| **Dependencias** | `curl_cffi` | `requests` | `requests` | `requests` |
| **Rate limit** | ⚠️ Agresivo | ⚠️ Bloqueos frecuentes | ✅ Permisivo | ⚠️ Freemium |
| **Confiabilidad** | ⚠️ CF puede romper | ⚠️ CF puede romper | ✅ Robusto | ✅ Robusto |
| **Slugs auto-discovery** | ✅ Sitemaps | ❌ Hardcoded | ❌ Hardcoded | ✅ API |

**Recomendacion:**
- **Coverage maximo:** investing.com (casi todo)
- **US opciones/futuros:** cboe-data
- **US stocks + opciones:** yahoo-finance
- **Fundamentals US detallados:** sec-data, finnhub
- **Macro US:** fred-macro
- **AR real-time:** data912
- **Confiabilidad maxima:** cboe-data (sin CF, gratis, sin auth)

---

## Changelog

### 2026-06-04 — v0.1.0 (inicial)

- ✅ Extraccion de cotizaciones (quote) con regex sobre HTML
- ✅ Historico OHLCV desde tabla HTML
- ✅ Sitemaps publicos como catalogo (10 categorias, 250K+ instrumentos)
- ✅ Busqueda fuzzy sobre sitemaps
- ✅ Profile, financials (income/balance/cashflow), ratios
- ✅ Dividends, earnings
- ✅ Auto-deteccion de tipo (commodities → equities)
- ✅ Retry con backoff exponencial
- ✅ Documentacion de slugs AR/LatAm

### Pendiente

- ❌ Opciones chains (JS dinamico, requiere browser)
- ❌ Insider trading (pagina separada)
- ❌ Analyst recommendations (pagina separada)
- ❌ Stock screener
- ❌ Comparador de instrumentos
