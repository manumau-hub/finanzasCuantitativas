---
name: fred-macro
description: "API gratuita de la Reserva Federal (FRED): 840K+ series macroeconómicas (GDP, CPI, tasas, empleo, M2, VIX, treasuries)."
license: MIT
metadata:
  category: finanzas, api, macroeconomia, federal-reserve, eeUU
  language: es
  source: https://fred.stlouisfed.org/docs/api/fred/
---

# FRED Macro — Federal Reserve Economic Data API

API **gratuita y oficial** de la Reserva Federal de St. Louis (FRED) con **840,000+ series temporales** macroeconómicas: PIB, inflación (CPI/PCE), tasas de interés, empleo, M2, VIX, treasuries, hipotecas y más.

**Base URL:** `https://api.stlouisfed.org/fred`
**Documentación oficial:** [fred.stlouisfed.org/docs/api/fred/](https://fred.stlouisfed.org/docs/api/fred/)

---

## Autenticación

### Obtener API Key (GRATIS)

1. Ir a: https://fred.stlouisfed.org/docs/api/api_key.html
2. Crear cuenta gratuita (email + contraseña)
3. Solicitar API key (se genera instantáneamente)
4. **No requiere tarjeta de crédito**

### Usar la API Key

```python
import os
API_KEY = os.getenv("FRED_API_KEY")  # Recomendado
# o directamente para pruebas:
# API_KEY = "TU_API_KEY_AQUI"
```

**⚠️ NUNCA hardcodear la API key en código compartido/commits.**

---

## Rate Limits

| Límite | Valor |
|--------|-------|
| **Requests por minuto** | 120 req/min |
| **Requests por día** | Ilimitado (sin límite diario explícito) |
| **Máx observaciones por request** | 100,000 |
| **Máx series por request** | Depende del endpoint (generalmente 1) |
| **Costo** | **Completamente GRATIS** |

### Recomendaciones

- Cachear respuestas localmente (los datos macroeconómicos cambian con poca frecuencia)
- Usar `observation_start` y `observation_end` para limitar rangos
- Implementar retry con backoff si se recibe HTTP 429 (Too Many Requests)
- Para descargar muchas series, intercalar 0.5s entre requests

---

## Endpoints Principales

### Series y Observaciones

| Endpoint | Descripción | Auth |
|----------|-------------|------|
| `GET /fred/series/observations` | Valores históricos de una serie | API Key |
| `GET /fred/series/search` | Buscar series por texto | API Key |
| `GET /fred/series` | Metadatos de una serie | API Key |
| `GET /fred/series/categories` | Categorías de una serie | API Key |
| `GET /fred/series/release` | Release asociado a una serie | API Key |

### Categorías y Releases

| Endpoint | Descripción |
|----------|-------------|
| `GET /fred/category` | Información de una categoría |
| `GET /fred/category/children` | Subcategorías |
| `GET /fred/category/related` | Categorías relacionadas |
| `GET /fred/category/series` | Series en una categoría |
| `GET /fred/release` | Información de un release |
| `GET /fred/release/dates` | Fechas de un release |
| `GET /fred/release/series` | Series en un release |

### Tags (etiquetas)

| Endpoint | Descripción |
|----------|-------------|
| `GET /fred/tags` | Buscar tags |
| `GET /fred/related_tags` | Tags relacionados |
| `GET /fred/tags/series` | Series con un tag específico |
| `GET /fred/series/tags` | Tags de una serie |

### Fuentes (Sources)

| Endpoint | Descripción |
|----------|-------------|
| `GET /fred/sources` | Lista de fuentes de datos |
| `GET /fred/source` | Información de una fuente |

### Mapas de Calendario

| Endpoint | Descripción |
|----------|-------------|
| `GET /fred/series/updates` | Series actualizadas recientemente |
| `GET /fred/seasonal/adjustments` | Opciones de ajuste estacional |

---

## Formato de Respuesta

Por defecto devuelve XML. Se puede cambiar con `&file_type=json`:

```json
{
  "realtime_start": "2026-06-01",
  "realtime_end": "2026-06-01",
  "observation_start": "1954-07-01",
  "observation_end": "2026-06-01",
  "units": "lin",
  "count": 864,
  "observations": [
    {
      "realtime_start": "2026-06-01",
      "realtime_end": "2026-06-01",
      "date": "1954-07-01",
      "value": "."
    },
    {
      "realtime_start": "2026-06-01",
      "realtime_end": "2026-06-01",
      "date": "1954-10-01",
      "value": "126.8"
    }
  ]
}
```

> **Nota:** valores `"."` indican dato no disponible (N/A).

---

## Categorías de Series

Las series FRED están organizadas en **categorías** (ids numéricos):

| ID | Categoría | Ejemplos |
|----|-----------|----------|
| 0 | Todas las categorías (raíz) | — |
| 32991 | **Population, Employment, & Labor Markets** | UNRATE, PAYEMS, NFP |
| 32992 | **National Income & Product Accounts** | GDP, GDPC1, GNP |
| 32993 | **Consumer Price Indexes (CPI)** | CPIAUCSL, CPILFESL |
| 32994 | **Producer Price Indexes (PPI)** | PPIACO, PPIFIS |
| 32995 | **Interest Rates** | FEDFUNDS, DGS10, DGS2 |
| 32996 | **Money, Banking, & Finance** | M2SL, M1SL, TOTBKCR |
| 32997 | **International Trade** | BOPGSTB |
| 33000 | **U.S. Regional Data** | Estadísticas estatales |
| 33001 | **Academic Data** | Datos académicos |

Ver referencia completa en [references/SERIES_REFERENCE.md](./references/SERIES_REFERENCE.md).

---

## Uso Rápido

### 1. Descargar una serie (Python)

```python
import requests

API_KEY = "TU_API_KEY"
url = "https://api.stlouisfed.org/fred/series/observations"
params = {
    "series_id": "GDP",
    "api_key": API_KEY,
    "file_type": "json",
    "observation_start": "2020-01-01",
    "observation_end": "2025-12-31"
}
r = requests.get(url, params=params)
data = r.json()
for obs in data["observations"]:
    if obs["value"] != ".":
        print(obs["date"], obs["value"])
```

### 2. Buscar series por palabra clave

```python
params = {
    "api_key": API_KEY,
    "file_type": "json",
    "search_text": "inflation",
    "search_type": "full_text",  # o "series_id"
    "limit": 10
}
r = requests.get("https://api.stlouisfed.org/fred/series/search", params=params)
```

### 3. Usando pandas

```python
import pandas as pd
import requests

def fetch_fred(series_id, api_key, start="2020-01-01"):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series_id, "api_key": api_key,
              "file_type": "json", "observation_start": start}
    r = requests.get(url, params=params)
    df = pd.DataFrame(r.json()["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df.set_index("date")["value"]

gdp = fetch_fred("GDP", API_KEY)
cpi = fetch_fred("CPIAUCSL", API_KEY)
fedfunds = fetch_fred("FEDFUNDS", API_KEY)
```

---

## Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| **[fetch_series.py](./scripts/fetch_series.py)** | Descarga una o más series FRED en CSV/JSON/Parquet |
| **[search_series.py](./scripts/search_series.py)** | Busca series FRED por texto, categoría o tag |
| **[download_multiple.py](./scripts/download_multiple.py)** | Descarga batches de series predefinidas por categoría |

---

## Series Esenciales (Headlines)

| Serie | Descripción | Frecuencia |
|-------|-------------|------------|
| `GDP` | PIB Nominal (Billions $) | Trimestral |
| `GDPC1` | PIB Real (Billions chained $) | Trimestral |
| `CPIAUCSL` | IPC General (CPI All Items) | Mensual |
| `CPILFESL` | IPC Subyacente (Core CPI) | Mensual |
| `PCEPILFE` | PCE Subyacente (Core PCE) | Mensual |
| `FEDFUNDS` | Tasa de Fondos Federales | Diaria |
| `DFF` | Tasa de Fondos Federales (efectiva) | Diaria |
| `DGS10` | Treasury a 10 años | Diaria |
| `DGS2` | Treasury a 2 años | Diaria |
| `T10Y2Y` | Spread 10y-2y (curva invertida) | Diaria |
| `UNRATE` | Tasa de Desempleo | Mensual |
| `PAYEMS` | Nóminas no agrícolas (Nonfarm Payrolls) | Mensual |
| `M2SL` | M2 Money Supply | Mensual |
| `M1SL` | M1 Money Supply | Mensual |
| `VIXCLS` | VIX (volatilidad S&P 500) | Diaria |
| `BAA10Y` | Spread BAA - 10y (credit spread) | Diaria |
| `TOTALSA` | Ventas Minoristas | Mensual |
| `INDPRO` | Producción Industrial | Mensual |
| `HOUST` | Viviendas Iniciadas | Mensual |
| `MORTGAGE30US` | Tasa Hipoteca 30 años | Semanal |

Referencia completa: **[references/SERIES_REFERENCE.md](./references/SERIES_REFERENCE.md)** (100+ series documentadas).

---

## Buenas Prácticas

1. **Cachear datos**: los datos macro no cambian frecuentemente; guardar en Parquet/CSV local
2. **Usar `file_type=json`**: más fácil de parsear que XML
3. **Filtrar por fecha**: usar `observation_start` para evitar descargar historia innecesaria
4. **Manejar valores `"."`**: representan datos no disponibles (NaN)
5. **Rate limiting**: 120 req/min = 1 request cada 0.5s como mínimo
6. **API Key**: usar variable de entorno `FRED_API_KEY`
7. **Citar fuente**: obligatorio incluir "This product uses the FRED API but is not endorsed or certified by the Federal Reserve Bank of St. Louis" en apps comerciales
