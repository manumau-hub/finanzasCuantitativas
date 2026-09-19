# RESPONSE FORMAT — Schema completo del JSON y CSV

> Documentacion del formato de respuesta de la API series-tiempo-ar, con
> todos los campos explicados y los 4 niveles de `metadata` comparados.

---

## Indice

1. [Schema general del response JSON](#1-schema-general-del-response-json)
2. [Campo `data`: formato columnar](#2-campo-data-formato-columnar)
3. [Campo `meta`: niveles de metadata](#3-campo-meta-niveles-de-metadata)
4. [Campo `params`: query echo](#4-campo-params-query-echo)
5. [Formato CSV](#5-formato-csv)
6. [Response normalizado (lo que devuelve el script)](#6-response-normalizado-lo-que-devuelve-el-script)
7. [Error responses](#7-error-responses)

---

## 1. Schema general del response JSON

```json
{
  "data": [...],         // array columnar de datapoints
  "count": 121,           // total datapoints disponibles (no necesariamente los devueltos)
  "meta": [...],          // metadata global + por serie
  "params": {...}         // echo de los params recibidos
}
```

### Top-level fields

| Field | Tipo | Descripcion |
|-------|------|-------------|
| `data` | array | Array columnar de datapoints. Cada row es `[date, value1, value2, ...]`. |
| `count` | int | Total de datapoints **disponibles en la serie**, no los devueltos en este request. |
| `meta` | array | Metadata: posicion [0] = global, posicion [1+] = una por cada serie. |
| `params` | object | Echo de los params recibidos (util para debugging). |

---

## 2. Campo `data`: formato columnar

El campo `data` es siempre un **array de arrays**:

```json
"data": [
  ["2026-02-01", 0.0290, 105.7],
  ["2026-03-01", 0.0338, 109.0],
  ["2026-04-01", 0.0258, 113.2]
]
```

### Estructura de cada row

```
[date, valor_serie_1, valor_serie_2, ..., valor_serie_N]
```

- **Columna 0:** Fecha como string `YYYY-MM-DD`.
- **Columnas 1..N:** Valores de cada serie, en el mismo orden que pasaste en `ids`.

### Single-serie

```bash
?ids=145.3_INGNACUAL_DICI_M_38
```

```json
"data": [
  ["2026-02-01", 0.0290],
  ["2026-03-01", 0.0338],
  ["2026-04-01", 0.0258]
]
```

Cada row tiene 2 elementos: fecha + valor.

### Multi-serie

```bash
?ids=145.3_INGNACUAL_DICI_M_38,158.1_REPTE_0_0_5
```

```json
"data": [
  ["2026-02-01", 0.0290, 1500000.0],
  ["2026-03-01", 0.0338, 1600000.0],
  ["2026-04-01", 0.0258, 1775664.12]
]
```

Cada row tiene 3 elementos: fecha + valor_serie_1 + valor_serie_2.

### Datapoints null

Si una serie no tiene dato en un periodo (ej: `last=12` de una serie
con menos de 12 datos), aparece `null`:

```json
"data": [
  ["2024-01-01", null],
  ["2024-02-01", 0.045],
  ["2024-03-01", 0.052]
]
```

### Valores tipados

- **Valores numericos:** float o int (JSON-style).
- **Porcentajes:** en formato decimal (ej: `0.025` = 2.5%, NO `2.5`).
- **Pesos / monedas:** sin separador de miles, con `.` como decimal.

---

## 3. Campo `meta`: niveles de metadata

`meta` es un array. El primer elemento es **global**, los siguientes son
**uno por cada serie**.

### Estructura

```json
"meta": [
  {global},
  {serie_1},
  {serie_2},
  ...
]
```

### `meta[0]` — Global

```json
{
  "frequency": "month",
  "start_date": "2026-02-01",
  "end_date": "2026-04-01"
}
```

| Field | Descripcion |
|-------|-------------|
| `frequency` | Frecuencia comun de todas las series ("day", "month", "quarter", etc.). |
| `start_date` | Fecha del primer datapoint devuelto. |
| `end_date` | Fecha del ultimo datapoint devuelto. |

### `meta[1..N]` — Por serie

Con `metadata=full` (default):

```json
{
  "catalog": {
    "title": "Datos Programacion Macroeconomica",
    "identifier": "sspm",
    "publisher": {"name": "...", "mbox": "..."}
  },
  "dataset": {
    "title": "Indice de Precios al Consumidor Nacional (IPC). Base diciembre 2016.",
    "description": "...",
    "issued": "2017-09-28",
    "modified": "2026-05-15",
    "source": "Instituto Nacional de Estadistica y Censos (INDEC)",
    "publisher": {...},
    "theme": ["precios"],
    "language": ["spa"]
  },
  "distribution": {
    "title": "Indice de precios al consumidor nivel general — variacion mensual",
    "downloadURL": "https://infra.datos.gob.ar/catalog/sspm/dataset/145/distribution/145.3/download/indice-precios-al-consumidor-nivel-general-base-diciembre-2016-mensual.csv",
    "format": "CSV",
    "issued": "2017-09-28"
  },
  "field": {
    "id": "145.3_INGNACUAL_DICI_M_38",
    "description": "IPC. Tasa de variacion mensual. Nivel General. Nacional. Base dic 2016.",
    "units": "Variacion intermensual",
    "representation_mode": "value",
    "representation_mode_units": "Variacion intermensual"
  }
}
```

### Niveles de metadata

| `metadata=` | Que incluye |
|-------------|-------------|
| `none` | NADA — solo `data` y `count`. Response mas compacto. |
| `only` | Solo `meta`, NO `data`. Util para inspeccionar series. |
| `simple` | `data` + `meta` REDUCIDO: solo `field` con id/description/units y `dataset` con title/source/issued. |
| `full` | `data` + `meta` COMPLETO con catalog/dataset/distribution/field todos completos. **DEFAULT**. |

### Recomendacion

Para uso programatico normal, **`metadata=simple` es el sweet spot**:
mantiene la info esencial (units, source, description) sin overhead.

---

## 4. Campo `params`: query echo

Devuelve los parametros que recibio el server (utiles para debugging):

```json
"params": {
  "ids": "145.3_INGNACUAL_DICI_M_38",
  "limit": "3",
  "identifiers": [
    {
      "id": "145.3_INGNACUAL_DICI_M_38",
      "distribution": "145.3",
      "dataset": "145"
    }
  ]
}
```

`identifiers` es un parseo del ID descomponiendo dataset y distribution.

---

## 5. Formato CSV

`?format=csv` devuelve un CSV plano. Headers configurables con `header=`:

### `header=titles` (default)

```csv
indice_tiempo,IPC_var_mensual
2026-02-01,0.0290
2026-03-01,0.0338
2026-04-01,0.0258
```

### `header=ids`

```csv
indice_tiempo,145.3_INGNACUAL_DICI_M_38
2026-02-01,0.0290
```

### `header=descriptions`

```csv
indice_tiempo,IPC. Tasa de variación mensual. Nivel General. Nacional. Base dic 2016.
2026-02-01,0.0290
```

### Multi-serie CSV

```csv
indice_tiempo,IPC_var_mensual,RIPTE
2026-02-01,0.0290,1500000.0
2026-03-01,0.0338,1600000.0
```

### Caracteristicas

- **Encoding:** UTF-8.
- **Separator:** coma `,`.
- **Decimal:** punto `.`.
- **Fechas:** ISO `YYYY-MM-DD`.
- **Sin metadata:** los headers tienen el titulo/id, pero no hay `units`,
  `source`, etc. Para metadata usar JSON.

### Pandas read

```python
import pandas as pd
URL = "https://apis.datos.gob.ar/series/api/series?ids=145.3_INGNACUAL_DICI_M_38&format=csv"
df = pd.read_csv(URL, parse_dates=['indice_tiempo'])
```

---

## 6. Response normalizado (lo que devuelve el script)

El script `fetch_indec.py` **transforma el response columnar a un dict
mas usable** con `normalize_series_response()`.

### Antes (raw API)

```json
{
  "data": [["2026-04-01", 0.0258]],
  "count": 112,
  "meta": [
    {"frequency": "month", "start_date": "...", "end_date": "..."},
    {"catalog": {...}, "dataset": {...}, "distribution": {...}, "field": {...}}
  ]
}
```

### Despues (normalizado por el script)

```json
{
  "count": 112,
  "frequency": "month",
  "start_date": "2026-02-01",
  "end_date": "2026-04-01",
  "n_series": 1,
  "series": [
    {
      "id": "145.3_INGNACUAL_DICI_M_38",
      "description": "IPC. Tasa de variacion mensual...",
      "units": "Variacion intermensual",
      "representation_mode": "value",
      "representation_mode_units": "Variacion intermensual",
      "frequency": null,
      "dataset_title": "Indice de Precios al Consumidor Nacional (IPC)...",
      "source": "Instituto Nacional de Estadistica y Censos (INDEC)",
      "issued": "2017-09-28",
      "distribution_url": "https://infra.datos.gob.ar/.../indice-precios-...csv",
      "data": [
        {"date": "2026-02-01", "value": 0.0290},
        {"date": "2026-03-01", "value": 0.0338},
        {"date": "2026-04-01", "value": 0.0258}
      ]
    }
  ]
}
```

### Beneficios de la normalizacion

- ✅ Cada serie es un dict con metadata + data **inline**.
- ✅ Data es lista de dicts `{"date", "value"}` en vez de tuplas posicionales.
- ✅ Multi-serie: array `series[]` separado, mas facil de iterar.
- ✅ Frecuencia y fechas globales **promovidas al top-level**.

### Para forzar response raw

```bash
py scripts/fetch_indec.py series "ID" --raw
```

O en Python:

```python
fetch_series(ID, raw=True)
```

---

## 7. Error responses

### HTTP 400 — Bad Request

```json
{
  "errors": [
    {"error": "El parametro last no puede ser utilizado junto a sort, start, limit"}
  ]
}
```

**Causas tipicas:**
- Combinar `last` con `sort/start/limit` (ver [PARAMS.md](./PARAMS.md)).
- `collapse` a frecuencia mayor que la serie (ej: serie mensual → daily).
- `start_date > end_date`.
- `representation_mode` invalido.

### HTTP 404 — Not Found

```json
{
  "errors": [
    {"error": "Serie con ID 'XXX_YYY' no encontrada"}
  ]
}
```

**Causas:**
- ID inexistente o con typo.
- Solucion: validar con `/validate` antes o buscar con `/search`.

### HTTP 500 — Internal Server Error

Raro pero ocurre. Reintentar con backoff.

### Estructura de error

```json
{
  "errors": [
    {"error": "descripcion humana"},
    {"error": "otra descripcion"}
  ]
}
```

Siempre lista (puede haber multiples errores). El script captura
`requests.HTTPError` y muestra el body.

### Catch en Python

```python
import requests
try:
    data = fetch_series("XXX_YYY")
except requests.HTTPError as e:
    if e.response.status_code == 404:
        print("ID no existe")
    elif e.response.status_code == 400:
        errors = e.response.json().get('errors', [])
        for err in errors:
            print(f"Error: {err['error']}")
    else:
        raise
```
