# FRED API Reference

Documentación detallada de la API de Federal Reserve Economic Data (FRED).

**Base URL:** `https://api.stlouisfed.org/fred`  
**Formato:** XML (default) o JSON (`&file_type=json`)  
**Auth:** API Key via `&api_key=YOUR_KEY` o header `X-API-KEY`

---

## Endpoints Detallados

### 1. Series > Observations — `GET /fred/series/observations`

**Descripción:** Valores históricos de una serie temporal.

**Parámetros:**

| Parámetro | Requerido | Default | Descripción |
|-----------|-----------|---------|-------------|
| `series_id` | ✅ | — | ID de la serie (ej: `GDP`, `UNRATE`) |
| `api_key` | ✅ | — | API Key |
| `file_type` | ❌ | `xml` | `json` para JSON |
| `observation_start` | ❌ | Desde inicio | Fecha inicio `YYYY-MM-DD` |
| `observation_end` | ❌ | Hoy | Fecha fin `YYYY-MM-DD` |
| `units` | ❌ | `lin` | `lin`=lineal, `chg`=cambio, `ch1`=cambio% anual, `pch`=cambio%, `pc1`=cambio% anual, `pca`=cambio% compuesto anual, `log`=log natural |
| `frequency` | ❌ | Original | `d`, `w`, `bw`, `m`, `q`, `sa`, `a` |
| `aggregation_method` | ❌ | `avg` | `avg`, `sum`, `eop` (end of period) |
| `output_type` | ❌ | 1 | 1=observaciones, 2=serie |
| `sort_order` | ❌ | `asc` | `asc`, `desc` |
| `limit` | ❌ | 100000 | Máx 100000 |
| `offset` | ❌ | 0 | Paginación |

**Ejemplo completo:**

```python
import requests

url = "https://api.stlouisfed.org/fred/series/observations"
params = {
    "series_id": "FEDFUNDS",
    "api_key": "YOUR_API_KEY",
    "file_type": "json",
    "observation_start": "2023-01-01",
    "observation_end": "2024-01-01",
    "units": "lin",
    "frequency": "m",
    "aggregation_method": "avg",
    "sort_order": "asc"
}
r = requests.get(url, params=params)
data = r.json()
print(f"Total observaciones: {data['count']}")
for obs in data["observations"]:
    if obs["value"] != ".":
        print(f"{obs['date']} → {obs['value']}")
```

**Respuesta JSON:**

```json
{
  "realtime_start": "2026-06-03",
  "realtime_end": "2026-06-03",
  "observation_start": "2023-01-01",
  "observation_end": "2024-01-01",
  "units": "lin",
  "output_type": 1,
  "file_type": "json",
  "order": "asc",
  "count": 12,
  "observations": [
    {"realtime_start": "2026-06-03", "realtime_end": "2026-06-03", "date": "2023-01-01", "value": "4.33"},
    {"realtime_start": "2026-06-03", "realtime_end": "2026-06-03", "date": "2023-02-01", "value": "4.50"},
    {"realtime_start": "2026-06-03", "realtime_end": "2026-06-03", "date": "2023-03-01", "value": "4.73"}
  ]
}
```

---

### 2. Series > Search — `GET /fred/series/search`

**Descripción:** Buscar series por texto.

**Parámetros:**

| Parámetro | Requerido | Default | Descripción |
|-----------|-----------|---------|-------------|
| `api_key` | ✅ | — | API Key |
| `search_text` | ✅ | — | Texto a buscar |
| `search_type` | ❌ | `full_text` | `full_text` o `series_id` |
| `realtime_start` | ❌ | Hoy | — |
| `realtime_end` | ❌ | Hoy | — |
| `limit` | ❌ | 100 | Máx 1000 |
| `offset` | ❌ | 0 | Paginación |
| `order_by` | ❌ | `search_rank` | `search_rank`, `series_id`, `title`, `popularity` |
| `sort_order` | ❌ | `desc` | `asc`, `desc` |
| `filter_variable` | ❌ | — | `frequency`, `units`, `seasonal_adjustment` |
| `filter_value` | ❌ | — | Valor del filtro |

**Ejemplo:**

```python
params = {
    "api_key": API_KEY,
    "file_type": "json",
    "search_text": "GDP",
    "search_type": "full_text",
    "limit": 10,
    "order_by": "popularity",
    "sort_order": "desc"
}
r = requests.get("https://api.stlouisfed.org/fred/series/search", params=params)
```

---

### 3. Series > Metadata — `GET /fred/series`

**Descripción:** Metadatos de una serie específica.

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `series_id` | ✅ | ID de la serie |

**Respuesta:**

```json
{
  "seriess": [{
    "id": "UNRATE",
    "realtime_start": "2026-06-03",
    "realtime_end": "2026-06-03",
    "title": "Unemployment Rate",
    "observation_start": "1948-01-01",
    "observation_end": "2026-05-01",
    "frequency": "Monthly",
    "frequency_short": "M",
    "units": "Percent",
    "units_short": "%",
    "seasonal_adjustment": "Seasonally Adjusted",
    "seasonal_adjustment_short": "SA",
    "last_updated": "2026-05-06 09:11:22-05",
    "popularity": 99,
    "notes": "..."
  }]
}
```

---

### 4. Series > Categories — `GET /fred/series/categories`

**Descripción:** Categorías a las que pertenece una serie.

| Parámetro | Requerido |
|-----------|-----------|
| `series_id` | ✅ |

```python
params = {"api_key": API_KEY, "file_type": "json", "series_id": "UNRATE"}
r = requests.get("https://api.stlouisfed.org/fred/series/categories", params=params)
# response: {"categories": [{"id": 32991, "name": "..."}]}
```

---

### 5. Categorías > Get — `GET /fred/category`

**Descripción:** Información de una categoría.

| Parámetro | Requerido | Default |
|-----------|-----------|---------|
| `category_id` | ✅ | — |

---

### 6. Categorías > Children — `GET /fred/category/children`

**Descripción:** Subcategorías de una categoría.

| Parámetro | Requerido | Default |
|-----------|-----------|---------|
| `category_id` | ✅ | — |

---

### 7. Categorías > Series — `GET /fred/category/series`

**Descripción:** Series dentro de una categoría.

| Parámetro | Requerido | Default |
|-----------|-----------|---------|
| `category_id` | ✅ | — |
| `limit` | ❌ | 100 |
| `offset` | ❌ | 0 |

**Ejemplo — listar todas las series de tasas de interés:**

```python
params = {"api_key": API_KEY, "file_type": "json", "category_id": 32995, "limit": 100}
r = requests.get("https://api.stlouisfed.org/fred/category/series", params=params)
```

---

### 8. Tags — `GET /fred/tags` y `GET /fred/related_tags`

**Descripción:** Buscar y navegar tags.

```python
# Todos los tags financieros populares
params = {"api_key": API_KEY, "file_type": "json",
          "tag_names": "money;interest rate", "order_by": "popularity"}
r = requests.get("https://api.stlouisfed.org/fred/tags", params=params)
```

---

### 9. Tags > Series — `GET /fred/tags/series`

**Descripción:** Series que tienen tags específicos.

```python
# Series con tags "monthly" + "inflation"
params = {"api_key": API_KEY, "file_type": "json",
          "tag_names": "monthly;inflation", "limit": 50}
r = requests.get("https://api.stlouisfed.org/fred/tags/series", params=params)
```

---

### 10. Sources — `GET /fred/sources` y `GET /fred/source`

**Descripción:** Fuentes de datos (BLS, BEA, Fed, etc.)

```python
# Todas las fuentes
r = requests.get("https://api.stlouisfed.org/fred/sources",
                 params={"api_key": API_KEY, "file_type": "json"})

# Fuente específica (source_id=1 = BLS)
r = requests.get("https://api.stlouisfed.org/fred/source",
                 params={"api_key": API_KEY, "file_type": "json", "source_id": 1})
```

| source_id | Nombre |
|-----------|--------|
| 1 | U.S. Bureau of Labor Statistics (BLS) |
| 2 | U.S. Bureau of Economic Analysis (BEA) |
| 3 | Federal Reserve Board |
| 6 | U.S. Census Bureau |
| 19 | U.S. Department of the Treasury |
| 31 | Freddie Mac |

---

### 11. Releases — `GET /fred/release`

**Descripción:** Releases (publicaciones de datos económicos).

```python
# Release del Employment Situation
params = {"api_key": API_KEY, "file_type": "json", "release_id": 50}
r = requests.get("https://api.stlouisfed.org/fred/release", params=params)
```

| release_id | Release |
|-----------|---------|
| 9 | Employment Situation (BLS) |
| 10 | Consumer Price Index (BLS) |
| 18 | GDP (BEA) |
| 50 | Federal Reserve FOMC |
| 53 | H.8 Assets and Liabilities |
| 55 | H.4.1 Factors Affecting Reserve Balances |
| 93 | Industrial Production (G.17) |

---

## Parámetros Comunes

### Units (transformaciones)

| Valor | Descripción |
|-------|-------------|
| `lin` | Datos originales (default) |
| `chg` | Cambio absoluto |
| `ch1` | Cambio absoluto año anterior |
| `pch` | Cambio porcentual |
| `pc1` | Cambio porcentual año anterior |
| `pca` | Cambio porcentual compuesto anual |
| `log` | Log natural |

### Frequency (cambio de frecuencia)

| Valor | Descripción |
|-------|-------------|
| `d` | Diaria |
| `w` | Semanal |
| `bw` | Bisemanal |
| `m` | Mensual |
| `q` | Trimestral |
| `sa` | Semestral |
| `a` | Anual |

### Aggregation Method (para cambio de frecuencia)

| Valor | Descripción |
|-------|-------------|
| `avg` | Promedio (default) |
| `sum` | Suma |
| `eop` | Fin de período |

---

## Códigos de Error HTTP

| Código | Significado | Solución |
|--------|-------------|----------|
| 200 | Success | — |
| 400 | Bad Request | Revisar parámetros |
| 401 | Unauthorized | API Key inválida |
| 403 | Forbidden | API Key no autorizada |
| 404 | Not Found | series_id no existe |
| 429 | Too Many Requests | Rate limit excedido (120/min) |
| 500 | Server Error | Error interno FRED |

### Ejemplo de error 400

```json
{
  "error_code": 400,
  "error_message": "Bad Request. Parameter 'series_id' is required."
}
```

---

## Estrategias de Rate Limiting

```python
import time
import requests

def fetch_fred_safe(series_id, api_key, retries=3):
    """Fetch con retry y backoff."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": "2020-01-01"
    }

    for attempt in range(retries):
        r = requests.get(url, params=params)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            wait = 2 ** attempt * 2  # 2, 4, 8 segundos
            print(f"Rate limit. Esperando {wait}s...")
            time.sleep(wait)
        else:
            r.raise_for_status()
    raise Exception(f"Failed after {retries} retries")
```

---

## Ejemplos Avanzados

### Múltiples series en paralelo (con rate limiting)

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_one(series_id, api_key):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series_id, "api_key": api_key,
              "file_type": "json", "observation_start": "2010-01-01",
              "limit": 1000}
    r = requests.get(url, params=params)
    time.sleep(1.0)  # rate limit
    return series_id, r.json()

def fetch_many(series_ids, api_key):
    results = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(fetch_one, sid, api_key): sid for sid in series_ids}
        for f in as_completed(futures):
            sid, data = f.result()
            results[sid] = data
    return results
```

### DataFrame con pandas

```python
import pandas as pd

def fred_to_df(series_id, api_key, start="2010-01-01"):
    """Descarga serie FRED y retorna Series de pandas."""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series_id, "api_key": api_key,
              "file_type": "json", "observation_start": start}
    r = requests.get(url, params=params)
    df = pd.DataFrame(r.json()["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    return df.set_index("date")["value"]

# Uso
gdp = fred_to_df("GDPC1", API_KEY)
gdp.plot(title="US Real GDP")
```

### Dashboard multi-serie

```python
import matplotlib.pyplot as plt

series = {
    "FEDFUNDS": "Federal Funds Rate",
    "DGS10": "Treasury 10y",
    "UNRATE": "Unemployment",
    "CPIAUCSL": "CPI Index"
}

dfs = {}
for sid, name in series.items():
    dfs[sid] = fred_to_df(sid, API_KEY)
    print(f"{name}: {len(dfs[sid])} obs")

# Normalizar y graficar
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for ax, (sid, name) in zip(axes.flat, series.items()):
    dfs[sid].plot(ax=ax, title=name)
plt.tight_layout()
plt.show()
```
