# Morningstar — Documentacion Tecnica

Documentacion completa del endpoint `/security/screener`, JSON schemas, troubleshooting, y comparacion con otras skills.

---

## Tabla de contenidos

1. [Descubrimiento del endpoint](#descubrimiento-del-endpoint)
2. [Endpoint detallado](#endpoint-detallado)
3. [JSON Schema de response](#json-schema-de-response)
4. [Universes y codigos](#universes-y-codigos)
5. [Data points (campos)](#data-points-campos)
6. [Encoding y localization](#encoding-y-localization)
7. [Rate limit y throttling](#rate-limit-y-throttling)
8. [PerformanceId: clave unica](#performanceid-clave-unica)
9. [Uso programatico](#uso-programatico)
10. [Troubleshooting](#troubleshooting)
11. [Limitaciones del skill](#limitaciones-del-skill)
12. [Endpoints NO accesibles (WAF)](#endpoints-no-accesibles-waf)
13. [Comparacion con otras skills](#comparacion-con-otras-skills)

---

## Descubrimiento del endpoint

El endpoint fue encontrado por **ingenieria inversa** observando las llamadas XHR que la UI web del screener de Morningstar (`tools.morningstar.co.uk/...`) hace al backend al filtrar y descargar la base de datos.

**URL descubierta:**
```
GET https://tools.morningstar.{co.uk,de,fr,it,es}/api/rest.svc/klr5zyak8x/security/screener
```

**Token `klr5zyak8x`:** es un token de la API interna. Es **universal** — funciona en los 5 sub-dominios `tools.morningstar.*` que no tienen WAF.

**Verificacion realizada (2026-06-04):**
- ✅ 53/77 universes probados devuelven data
- ✅ 5/5 sub-dominios funcionan con el mismo token
- ❌ `tools.morningstar.com` (US) — connection reset / IP geoblocked
- ❌ Otros sub-dominios (`com.au`, `br`, `jp`, `in`, `mx`, `ca`) — DNS fail / timeout

---

## Endpoint detallado

### URL pattern

```
https://tools.morningstar.{co.uk,de,fr,it,es}/api/rest.svc/klr5zyak8x/security/screener
```

### HTTP method

`GET` con query parameters.

### Query parameters

| Param | Required | Tipo | Default | Descripcion |
|-------|----------|------|---------|-------------|
| `page` | No | int | `1` | Numero de pagina |
| `pageSize` | No | int | `50000` | Tamano de pagina (maximo: 50000) |
| `sortOrder` | No | string | `Name asc` | Orden (`Name asc`, `Ticker asc`, etc.) |
| `outputType` | No | string | `json` | Formato (`json`) |
| `version` | No | int | `1` | Version de la API |
| `languageId` | **Si** | string | - | Idioma de respuesta (ver abajo) |
| `currencyId` | **Si** | string | - | Moneda de campos `ClosePrice`/`MarketCap` (ISO 4217) |
| `universeIds` | **Si** | string | - | Universe code con prefijo `E0EXG$` |
| `securityDataPoints` | **Si** | string | - | Lista de campos pipe-separated |
| `filters` | No | string | - | Filtros adicionales (sintaxis no documentada) |
| `term` | No | string | - | Busqueda fuzzy por nombre |
| `subUniverseId` | No | string | - | Sub-universo (vacio) |

### Headers (no obligatorios pero recomendados)

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.9
```

> Sin `Authorization`, sin cookies, sin CSRF token. El endpoint es publico.

### `languageId` soportados

`en-GB` (recomendado), `en-US`, `de-DE`, `fr-FR`, `it-IT`, `es-ES`, `pt-PT`, `nl-NL`, `ja-JP`, `zh-CN`, `zh-HK`, `ko-KR`, `fi-FI`, `el-GR`, `da-DK`, `no-NO`, `sv-SE`, `is-IS`, `et-EE`, `pl-PL`, `tr-TR`, `ru-RU`, `he-IL`, `th-TH`, `ms-MY`, `id-ID`, `en-PH`, `vi-VN`, `en-AU`, `en-NZ`, `en-ZA`, `en-SG`, `en-IE`, `en-CA`, `en-IN`, `es-MX`, `pt-BR`, `es-AR`, `es-CL`, `es-CO`, `es-PE`, `zh-TW`, `de-AT`, `de-CH`, `nl-BE`, `el-GR`, `ar-SA`, `ar-AE`, `ar-EG`, etc.

> **Problema de encoding:** los nombres de sectores/industrias vienen en el idioma del `languageId`, pero los caracteres acentuados (á, é, í, ó, ú, ñ) vienen mal-encodados en UTF-8. **Solucion:** usar `en-GB` siempre.

### `currencyId` soportados

Todos los ISO 4217: `USD`, `EUR`, `GBP`, `CHF`, `JPY`, `CNY`, `HKD`, `INR`, `BRL`, `ARS`, `MXN`, `CAD`, `AUD`, `NZD`, `SEK`, `NOK`, `DKK`, `ISK`, `PLN`, `TRY`, `ILS`, `ZAR`, `KRW`, `SGD`, `HKD`, `TWD`, `THB`, `MYR`, `IDR`, `PHP`, `CZK`, `HUF`, `RON`, `RUB`, `CLP`, `COP`, `PEN`, `EGP`, `AED`, `SAR`, `KES`, etc.

### Ejemplo de request

```bash
curl "https://tools.morningstar.co.uk/api/rest.svc/klr5zyak8x/security/screener?\
page=1&pageSize=10&outputType=json&version=1&languageId=en-GB&currencyId=USD&\
universeIds=E0EXG%24XNAS&securityDataPoints=Ticker%7CName%7CClosePrice%7CMarketCap&\
sortOrder=Name+asc&filters=&term=&subUniverseId="
```

### Ejemplo de response

```json
{
  "rows": [
    {
      "Ticker": "AAPL",
      "Name": "Apple Inc",
      "ClosePrice": 311.23,
      "MarketCap": 4571145807880
    },
    {
      "Ticker": "MSFT",
      "Name": "Microsoft Corp",
      ...
    }
  ]
}
```

> El response es **JSON nativo** (no envuelto). Es un array de objetos directamente.

---

## JSON Schema de response

### Estructura

```typescript
{
  rows: Array<{
    Ticker: string,
    Name: string,
    PerformanceId?: string,
    Universe?: string,
    MarketCountryName?: string,
    SectorName?: string,
    IndustryName?: string,
    EquityStyleBox?: number,  // 1-9
    QuantitativeStarRating?: number,  // 1-5
    ClosePrice?: number,
    MarketCap?: number,
    PERatio?: number,
    PEGRatio?: number,
    DividendYield?: number,
    DebtEquityRatio?: number,
    NetMargin?: number,
    EBTMarginYear1?: number,
    ROATTM?: number,
    ROETTM?: number,
    ROEYear1?: number,
    ROICYear1?: number,
    EPSGrowth3YYear1?: number,
    RevenueGrowth3Y?: number,
    ReturnD1?: number,
    ReturnW1?: number,
    ReturnM0?: number,
    ReturnM1?: number,
    ReturnM3?: number,
    ReturnM6?: number,
    ReturnM12?: number,
    ReturnM36?: number,
    ReturnM60?: number,
    ReturnM120?: number,
  }>
}
```

### Tipos de datos

| Tipo Python | Equivalente JSON | Notas |
|-------------|------------------|-------|
| `string` | `"Apple Inc"` | Siempre en UTF-8 (con bug en acentos) |
| `int` | `1234` | Enteros para EquityStyleBox, QuantitativeStarRating, etc. |
| `float` | `311.23` | Decimales con punto |
| `null` | `null` | **No aparece** en el JSON. Los campos faltantes se omiten completamente. |
| `NaN` | (no JSON valido) | Morningstar usa `Infinity`, `NaN` que **rompen** `json.dumps()`. Usar `default=str` en el dump. |

### Campos nullables

Aprox. 30-50% de los campos vienen como **`null`/omitidos** para CEDEARs, small caps, y stocks con data incompleta. Esto es normal, no es un error.

```python
import math
# En pandas:
df = pd.read_csv("ar.csv")
# Reemplazar NaN con None si es necesario
df = df.where(pd.notnull(df), None)
```

### Tamaño de response

- Un universe con 2,000 listings y 33 campos ≈ **1-2 MB** de JSON
- Todos los 53 universes ≈ **20-50 MB** de JSON
- El script puede manejarlo con `requests` sin problemas

---

## Universes y codigos

Ver [assets/UNIVERSES.md](../assets/UNIVERSES.md) para la lista completa.

**Resumen por region:**

| Region | # Universes | Total Listings |
|--------|-------------|----------------|
| Americas (US, CA, LatAm) | 9 | 13,985 |
| Europe | 27 | 65,206 |
| Asia | 13 | 33,479 |
| Oceania | 2 | 1,941 |
| Middle East & Africa | 2 | 878 |
| **TOTAL** | **53** | **102,093** |

---

## Data points (campos)

Ver [assets/DATA_POINTS.md](../assets/DATA_POINTS.md) para la lista completa.

**Resumen por categoria:**

| Categoria | # Campos | Ejemplos |
|----------|----------|----------|
| Metadata | 5 | Ticker, Name, PerformanceId, Universe, MarketCountryName |
| Categoricos | 4 | SectorName, IndustryName, EquityStyleBox, QuantitativeStarRating |
| Tamano/precio | 2 | ClosePrice, MarketCap |
| Valuacion | 3 | PERatio, PEGRatio, DividendYield |
| Calidad | 7 | DebtEquityRatio, NetMargin, EBTMarginYear1, ROATTM, ROETTM, ROEYear1, ROICYear1 |
| Crecimiento | 2 | EPSGrowth3YYear1, RevenueGrowth3Y |
| Retornos | 10 | ReturnD1/W1/M0/M1/M3/M6/M12/M36/M60/M120 |
| **TOTAL** | **33** | |

---

## Encoding y localization

### El problema

Cuando se pide `languageId=es-AR`, los nombres de sectores/industrias vienen con caracteres acentuados mal-encodados:

```json
{
  "SectorName": "Energía",   // OK, decoded: "Energía"
  "IndustryName": "Petróleo y Gas - Integrado"  // OK
}
```

PERO al imprimirlos en la consola Windows (cp1252):

```
Energía  -> Energ�a
Petróleo -> Petr�leo
```

La consola de Windows no puede imprimir `í` directamente. Si se redirige a archivo UTF-8, se ve bien.

### Solucion implementada

El script usa **`languageId=en-GB`** para todos los universes. Esto evita el problema de encoding y devuelve los nombres de sectores/industrias en inglés (que es el estándar para screener cuantitativo).

```python
# En fetch_universe():
"languageId": "en-GB",  # Forzado para todos los universes
"currencyId": meta["currency"],  # Moneda local del universe (ARS, BRL, etc.)
```

> **Trade-off:** los nombres de sectores vienen en inglés. Si necesitás nombres en español (Energía, Petróleo), podés:
> 1. Pedir `languageId=es-AR` y guardar el JSON con `ensure_ascii=False`
> 2. Hacer un post-proceso: mapear "Energy" → "Energía", "Oil & Gas Integrated" → "Petróleo y Gas Integrado", etc.
> 3. Usar la skill con un mapping local

---

## Rate limit y throttling

### Observaciones

- **Sin rate limit agresivo** observado para uso normal (1-10 requests)
- Hacer 50+ requests en pocos segundos puede triggerear throttling del CDN
- El script espera 0.5-1 segundo entre universes

### Headers de respuesta

- `Server`: CloudFront
- `Content-Type`: application/json
- Sin `X-RateLimit-*` headers

### Recomendaciones

```python
# En fetch_universe(), el script espera 0.5s despues de cada universe
time.sleep(0.5)

# Si haces --all (53 universes), total ~30-60 segundos
# Si haces un solo universe, ~1-5 segundos
```

### Errores tipicos

| Status | Causa | Solucion |
|--------|-------|----------|
| 200 + JSON | OK | - |
| 200 + HTML (CF challenge) | El sub-dominio tiene WAF (ej: `.com`, `.com.au`) | Usar otro sub-dominio |
| 404 | Universe no existe o no tiene data | Verificar `assets/UNIVERSES.md` |
| 500 | Error del servidor (raro) | Reintentar |
| Timeout | Red lenta o IP bloqueada | Esperar 1-2 min |

---

## PerformanceId: clave unica

### Que es

`PerformanceId` es un identificador unico de 12 caracteres que Morningstar asigna a cada **listing** (instrumento en un exchange especifico).

**Formato:** `0P0000XXXXX` o `0P0000ABCDE` (5 chars hex)

### Es estable?

- ✅ Estable en el tiempo (no cambia)
- ✅ Unico por listing
- ❌ NO se transfiere entre exchanges (mismo Apple tiene diferentes IDs)

### Ejemplo: Apple Inc en diferentes exchanges

| Exchange | Ticker | PerformanceId |
|----------|--------|---------------|
| NASDAQ (XNAS) | AAPL | `0P000000GY` |
| Frankfurt (XFRA) | APC | `0P0000EEDJ` |
| Brasil BDR (BVMF) | AAPL34 | `0P0000VE8R` |
| CEDEAR Argentina (XBUE) | AAPL | `0P0000TFNY` |

### Para hacer match entre universes

Si querés matchear datos entre universes (ej: Apple US vs Apple CEDEAR), **no** uses PerformanceId. Usa:
- `Ticker` + `MarketCountryName`
- O `Name` (limpieza, ej: lowercase, remove suffixes)
- O ISIN (no incluido en el screener, pero disponible en otros endpoints)

---

## Uso programatico

### Como libreria Python

```python
import sys
sys.path.insert(0, "scripts")
from fetch_morningstar import (
    make_session, fetch_universe, UNIVERSES, DATA_POINTS
)

s = make_session()

# Descargar un universe
rows = fetch_universe(s, "XNAS")
print(f"Total: {len(rows)}")
for row in rows[:3]:
    print(row["Ticker"], row["Name"], row.get("ClosePrice"))

# Filtrar manualmente
for row in rows:
    pe = row.get("PERatio")
    if pe and pe < 10 and row.get("MarketCap", 0) > 1e9:
        print(f"Value stock: {row['Ticker']} PE={pe:.1f}")
```

### Como subprocess

```bash
# Desde Python u otro lenguaje
import subprocess, json

result = subprocess.run(
    ["python", "fetch_morningstar.py", "search", "Apple", "--universe", "XNAS"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
print(data["results"])
```

### Integracion con pandas

```python
import subprocess, json
import pandas as pd

# Ejecutar script
result = subprocess.run(
    ["python", "fetch_morningstar.py", "screener", "--universe", "XNAS", "-q"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)

# A pandas
universe_data = data["universes"]["XNAS"]
df = pd.DataFrame(universe_data["rows"])
print(df.describe())
print(df.sort_values("MarketCap", ascending=False).head(10))
```

### Integracion con SQL

```python
# Cargar CSV a SQLite
import subprocess
import sqlite3

subprocess.run(["python", "fetch_morningstar.py", "screener",
                "--universe", "XBUE", "-o", "ar.csv"])

con = sqlite3.connect("morningstar.db")
import pandas as pd
df = pd.read_csv("ar.csv")
df.to_sql("argentina_listings", con, if_exists="replace", index=False)
print("Loaded", len(df), "rows to SQLite")
```

---

## Troubleshooting

### "Connection reset" o timeout

**Causa:** IP geoblocked o DNS no resuelve.

**Solucion:**
1. Verificar que estas usando uno de los 5 dominios soportados: `co.uk`, `de`, `fr`, `it`, `es`
2. Si estas fuera de Europa, probar con VPN
3. Esperar 5-10 minutos (el rate limit puede ser temporal)

### "No se encontro el universo XXXX"

**Causa:** Universe code incorrecto o no soportado.

**Solucion:**
- Ver `assets/UNIVERSES.md` para la lista completa
- Sin prefijo `E0EXG$` (el script lo agrega automaticamente)
- 53 universes soportados, 24 probados sin data (no usar)

### "Encoding error" en acentos

**Causa:** `languageId=es-XX` devuelve chars mal-encodados en UTF-8.

**Solucion:**
- El script YA fuerza `languageId=en-GB` para todos los universes
- Si necesitas nombres en español, post-procesar el JSON con un mapping local

### Output JSON invalido (NaN, Infinity)

**Causa:** Morningstar devuelve `NaN` y `Infinity` en algunos campos (ej: cuando `PERatio` es muy alto o indefinido). Python `json.dumps()` no los soporta.

**Solucion:**
```python
import math, json

def clean_for_json(obj):
    """Reemplaza NaN/Infinity con None."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(x) for x in obj]
    return obj

# Usar:
out = clean_for_json(out)
json.dumps(out, default=str)
```

> El script ya usa `default=str` que convierte `NaN` a string. Pero si querés `null` en su lugar, usar `clean_for_json()`.

### "429 Too Many Requests"

**Causa:** Demasiadas requests muy rapido.

**Solucion:**
- Reducir la velocidad: el script ya espera 0.5s entre universes
- Esperar 5-10 minutos
- Considerar usar un proxy

---

## Limitaciones del skill

1. **Solo el endpoint `/security/screener` es accesible.** No hay fundamentals por security, OHLCV, real-time, insider transactions, etc.
2. **Sin WAF bypass.** No podemos usar Selenium ni headless browsers en este skill.
3. **Sin datos puntuales.** El skill es para screening masivo, no para quote de un solo ticker (usar `investing` o `yahoo-finance`).
4. **5 sub-dominios solamente.** US, Australia, Brasil, etc. no funcionan.
5. **Encoding limitado.** Solo `en-GB` se ve bien. Otros idiomas tienen problemas de UTF-8.
6. **Sin paginación interna.** El `pageSize=50000` es el max. Si un universe tiene >50K listings (ej: `XFRA` con 14K anda, pero podria haber mas), hay que paginar manualmente.
7. **No es oficial.** El endpoint puede cambiar sin aviso. Si Morningstar decide descontinuarlo o moverlo, el skill se rompe.

---

## Endpoints NO accesibles (WAF)

Los siguientes endpoints de Morningstar existen pero **NO son accesibles** desde este skill (requieren resolver AWS WAF challenge):

### AWS WAF "Goku" challenge

```
Status: 202 Accepted
x-amzn-waf-action: challenge

<script>
  window.gokuProps = { "key": "<RSA>", "iv": "<IV>", "context": "<ciphertext>" };
</script>
<script src="https://...token.awswaf.com/.../challenge.js"></script>
```

Challenge cognitivo (3 retos en JS, cifrado RSA + AES). NO se puede resolver con `requests` puro. Requiere Selenium, Playwright, o undetected-chromedriver.

### Endpoints bloqueados

| URL | Status | Notas |
|-----|--------|-------|
| `https://global.morningstar.com/api/v1/{lang}/tools/screener/_data` | 202 WAF | Mismo screener que este skill, con WAF |
| `https://global.morningstar.com/api/v1/{lang}/stores/data-points/fields` | 202 WAF | Lista de TODOS los campos (no solo los 28) |
| `https://global.morningstar.com/api/v1/{lang}/stores/filters` | 202 WAF | Lista de TODOS los filtros disponibles |
| `https://api-global.morningstar.com/sal-service/v1/{asset}/{field}/{id}` | 401 WAF | Endpoints de fundamentals/quote |
| `https://lt.morningstar.com/api/rest.svc/{token}/security_details/{id}` | 500/401 | Detalles de security (no funciona) |
| `https://www.morningstar.com/api/v2/stores/realtime/{suffix}` | 404 WAF | Real-time quotes |
| `https://www.us-api.morningstar.com/QS-markets/chartservice/v2/timeseries` | 401 WAF | Time series OHLCV |

### Endpoints descubiertos en `mstarpy` v10 (WAF-blocked)

| Endpoint | Field | Descripcion |
|----------|-------|-------------|
| `/sal-service/v1/eq/equityOverview/{id}` | equityOverview | Resumen del stock |
| `/sal-service/v1/eq/quote/{id}` | quote | Cotizacion |
| `/sal-service/v1/eq/keyratios/{id}` | keyratios | Ratios clave |
| `/sal-service/v1/eq/valuation/v3/{id}` | valuation | Fair value |
| `/sal-service/v1/eq/keyMetrics/summary/{id}` | keyMetrics/summary | Metricas clave |
| `/sal-service/v1/eq/keyMetrics/financialHealth/{id}` | keyMetrics/financialHealth | Salud financiera |
| `/sal-service/v1/eq/keyMetrics/cashFlow/{id}` | keyMetrics/cashFlow | Cash flow metricas |
| `/sal-service/v1/eq/keyMetrics/profitabilityAndEfficiency/{id}` | keyMetrics/profitabilityAndEfficiency | Rentabilidad |
| `/sal-service/v1/eq/keyStats/growthTable/{id}` | keyStats/growthTable | Crecimiento |
| `/sal-service/v1/eq/morningstarTake/v3/{id}` | morningstarTake/v3 | Take de Morningstar |
| `/sal-service/v1/eq/morningstarTake/v4/{id}` | morningstarTake/v4 | Take v4 |
| `/sal-service/v1/eq/newfinancials/{id}` | newfinancials | Nuevos financials |
| `/sal-service/v1/eq/dividends/v4/{id}` | dividends/v4 | Dividendos |
| `/sal-service/v1/eq/esgRisk/{id}` | esgRisk | ESG |
| `/sal-service/v1/eq/esgRisk/sustainability/{id}` | esgRisk/sustainability | Sustainability |
| `/sal-service/v1/eq/ownership/v1/{id}` | ownership/v1 | Ownership |
| `/sal-service/v1/eq/insiders/boardOfDirectors/{id}` | insiders/boardOfDirectors | Board |
| `/sal-service/v1/eq/insiders/transactionHistory/{id}` | insiders/transactionHistory | Insider trades |
| `/sal-service/v1/eq/insiders/transactionChart/{id}` | insiders/transactionChart | Insider chart |
| `/sal-service/v1/eq/split/v1/{id}` | split/v1 | Splits |
| `/sal-service/v1/eq/trailingTotalReturns/{id}` | trailingTotalReturns | Retornos |
| `/sal-service/v1/eq/quotes/{id}` | quotes | Quote |

> **Para acceder a estos:** usar `mstarpy` v10 (que ya implementa el bypass con Selenium).

---

## Comparacion con otras skills

| Aspecto | Morningstar (este) | Investing.com | Yahoo Finance | CBOE Data |
|---------|---------------------|---------------|---------------|-----------|
| **Endpoint** | API JSON (`requests`) | HTML scrape (`curl_cffi`) | HTML scrape | API REST |
| **Auth** | None | None | None | None |
| **Cobertura** | 102K listings, 39 paises | 81K+ equities, 10K+ indices, 2.4K FX, 344 commodities, 30K+ ETFs, 4K+ crypto | 200K+ tickers | US indices, options, futures |
| **Quote por security** | ❌ Solo masivo | ✅ | ✅ | ✅ |
| **Historico OHLCV** | ❌ | ✅ | ✅ | ✅ |
| **Fundamentals puntuales** | ❌ | ✅ (income/balance/cashflow) | ✅ | ❌ |
| **Screening masivo** | ✅ (100K+ rows) | ❌ | ❌ | ❌ |
| **CEDEARs Argentina** | ✅ (XBUE) | ⚠️ (slugs limitados) | ⚠️ | ❌ |
| **Dependencias** | `requests` | `curl_cffi` | `requests` | `requests` |
| **Rate limit** | Bajo | Alto (CF) | Medio | Bajo |
| **Robustez** | ⚠️ Endpoint no oficial | ⚠️ CF puede romper | ⚠️ CF puede romper | ✅ Robusto |
| **Cobertura global** | ✅ Excelente | ✅ Excelente | ✅ Excelente | ❌ US only |

**Recomendacion de uso:**

| Caso de uso | Skill recomendada |
|-------------|-------------------|
| Descargar DB completa de un pais/region | **Morningstar** (este) |
| CEDEARs Argentina (BCBA) | **Morningstar** (este) |
| Screening masivo (filtrar 1000+ stocks) | **Morningstar** (este) |
| Quote de un ticker especifico | Investing / Yahoo / CBOE |
| Historico OHLCV | Investing / Yahoo / CBOE |
| Real-time quotes US | Alpaca Data / Finnhub |
| Real-time AR | Data912 |
| Options chains US | CBOE Data |
| Fundamentals US detallados | SEC Data / Finnhub |

---

## Changelog

### 2026-06-04 — v1.0.0 (inicial)

- ✅ Script `fetch_morningstar.py` con 5 modos: `info`, `fields`, `search`, `screener`, `download`
- ✅ 53 universes soportados (102,093 listings en 39 paises)
- ✅ 33 campos (5 metadata + 5 categoricos + 23 numericos)
- ✅ Multi-universe, multi-pais, multi-currency
- ✅ Output JSON y CSV
- ✅ Documentacion exhaustiva (SKILL.md + REFERENCE.md + assets/UNIVERSES.md + assets/DATA_POINTS.md)
- ✅ Token universal `klr5zyak8x` validado en 5 sub-dominios
- ✅ Encoding fix: usa `en-GB` para evitar problemas con acentos

### Pendiente (futuro)

- ❌ Bypass de AWS WAF (Selenium, Playwright) — para acceder a fundamentals/real-time
- ❌ Filtros server-side (`filters=` param) — actualmente solo `term` funciona
- ❌ Paginacion automatica para universes >50K listings
- ❌ Mas sub-dominios de tools.morningstar (US, AU, etc.) — actualmente bloqueados
