# ENDPOINTS — Deep dive de los 4 endpoints

> Documentacion detallada de cada uno de los 4 endpoints expuestos por
> la API `apis.datos.gob.ar/series/api/`.

---

## Indice

1. [`/series` — Fetch de datos](#1-series--fetch-de-datos)
2. [`/search` — Buscador full-text](#2-search--buscador-full-text)
3. [`/dump` — Descarga del catalogo completo](#3-dump--descarga-del-catalogo-completo)
4. [`/validate` — Validacion de queries](#4-validate--validacion-de-queries)
5. [Decidir que endpoint usar](#5-decidir-que-endpoint-usar)

---

## 1. `/series` — Fetch de datos

**URL:** `GET https://apis.datos.gob.ar/series/api/series`

Es el endpoint **principal**. Devuelve los datapoints de una o varias series
identificadas por sus IDs.

### Caso simple

```bash
GET /series?ids=145.3_INGNACUAL_DICI_M_38
```

Devuelve los ultimos datos de la serie "IPC nacional variacion mensual".

### Multi-serie en una llamada

```bash
GET /series?ids=145.3_INGNACUAL_DICI_M_38,158.1_REPTE_0_0_5
```

Devuelve datos de **2 series simultaneamente** (IPC mensual + RIPTE).

> **Importante:** las series del multi-call deben tener **misma frecuencia**
> o usar `collapse` para unificarlas. Si una es mensual y otra trimestral,
> los timestamps no van a alinearse y vas a ver `null` en columnas.

### Parametros

Ver lista completa en [PARAMS.md](./PARAMS.md). Resumen:

| Param | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| `ids` | string CSV | (requerido) | IDs separados por coma |
| `format` | enum | `json` | `json` o `csv` |
| `start_date` | YYYY-MM-DD | — | Filtro temporal desde |
| `end_date` | YYYY-MM-DD | — | Filtro temporal hasta |
| `representation_mode` | enum | `value` | Transformacion (ver [REPRESENTATION_MODES.md](./REPRESENTATION_MODES.md)) |
| `collapse` | enum | — | Agregacion temporal |
| `collapse_aggregation` | enum | `avg` | Modo de agregacion |
| `limit` | int | 100 | Datapoints por serie (max 1,000) |
| `start` | int | 0 | Offset para paginacion |
| `last` | int | — | Ultimos N valores (**INCOMPATIBLE con sort, start, limit**) |
| `sort` | enum | `asc` | `asc` o `desc` |
| `metadata` | enum | `full` | `none`, `only`, `simple`, `full` |
| `header` | enum | `titles` | Header del CSV |

### Response (JSON)

Ver schema completo en [RESPONSE_FORMAT.md](./RESPONSE_FORMAT.md).

```json
{
  "data": [
    ["2026-02-01", 0.0290],
    ["2026-03-01", 0.0338],
    ["2026-04-01", 0.0258]
  ],
  "count": 112,
  "meta": [
    {
      "frequency": "month",
      "start_date": "2026-02-01",
      "end_date": "2026-04-01"
    },
    {
      "catalog": {...},
      "dataset": {
        "title": "Indice de Precios al Consumidor Nacional (IPC). Base diciembre 2016.",
        "source": "Instituto Nacional de Estadistica y Censos (INDEC)",
        "issued": "2017-09-28"
      },
      "distribution": {
        "title": "...",
        "downloadURL": "https://infra.datos.gob.ar/.../indice-precios-..csv"
      },
      "field": {
        "id": "145.3_INGNACUAL_DICI_M_38",
        "description": "IPC. Tasa de variacion mensual. Nivel General. Nacional. Base dic 2016.",
        "units": "Variacion intermensual",
        "representation_mode": "value"
      }
    }
  ],
  "params": {...}
}
```

### Ejemplo: paginacion en serie larga

```bash
# Primeros 1000 valores
GET /series?ids=145.3_INGNACUAL_DICI_M_38&limit=1000&start=0

# Siguientes 1000
GET /series?ids=145.3_INGNACUAL_DICI_M_38&limit=1000&start=1000
```

### Ejemplo: filtrar por fechas

```bash
GET /series?ids=145.3_INGNACUAL_DICI_M_38&start_date=2020-01-01&end_date=2024-12-31
```

### Ejemplo: ultimos 12 meses

```bash
GET /series?ids=145.3_INGNACUAL_DICI_M_38&last=12
```

> ⚠️ Cuando uses `last`, **NO** pasar `start`, `limit` ni `sort` — la API
> los rechaza juntos con error 400 `"El parametro last no puede ser
> utilizado junto a sort, start, limit"`.

### Ejemplo: CSV

```bash
GET /series?ids=145.3_INGNACUAL_DICI_M_38&format=csv
```

Devuelve:

```csv
indice_tiempo,IPC_var_mensual
2016-04-01,0.0254
2016-05-01,0.0408
...
```

---

## 2. `/search` — Buscador full-text

**URL:** `GET https://apis.datos.gob.ar/series/api/search`

Buscador full-text sobre el catalogo de series. Devuelve IDs + metadata
para luego usar en `/series`.

### Parametros

| Param | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| `q` | string | (requerido) | Keywords a buscar |
| `limit` | int | 10 | Resultados por pagina (max no documentado, ~100 funciona) |
| `offset` | int | 0 | Paginacion |
| `aggregations[publisher.name]` | string | — | Filtro por publicador (ej: `INDEC`) |
| `aggregations[catalog.id]` | string | — | Filtro por catalogo |
| `aggregations[dataset.theme]` | string | — | Filtro por tema |

### Ejemplo basico

```bash
GET /search?q=ipc&limit=10
```

Devuelve:

```json
{
  "data": [
    {
      "field": {
        "id": "99.3_IR_2008_0_9",
        "description": "Indice de precios al consumidor IPC resto. Mensual",
        "frequency": "R/P1M",
        "units": "Indice abr-2008=100"
      },
      "dataset": {
        "title": "Indice de Precios al Consumidor GBA (IPC-GBA). Base abril 2008. SERIE DISCONTINUADA",
        "source": "Instituto Nacional de Estadistica y Censos (INDEC)"
      },
      "distribution": {...},
      "catalog": {...}
    },
    ...
  ],
  "meta": {
    "available": 4249,
    "limit": 10,
    "offset": 0,
    "total": 10
  }
}
```

### Tips de busqueda

1. **Series DISCONTINUADAS:** muchas series viejas (base 2008, 1974, etc.)
   estan marcadas como `SERIE DISCONTINUADA` en el `dataset.title`. Filtrar
   esas para usar las series activas.

2. **Keywords compuestas:** funcionan bien con multiples palabras.
   ```bash
   GET /search?q=ipc+nucleo+nacional   # IPC core nacional
   GET /search?q=emae+desestacionalizado   # EMAE deseasonalized
   ```

3. **No matchea por dataset_id ni distribution_id**, solo por descripcion y title.

### Tipico workflow

```python
# 1. Buscar
results = search("ipc nacional")
# 2. Filtrar las activas
active = [r for r in results['data'] if 'DISCONTI' not in r['dataset']['title']]
# 3. Tomar el primer ID
sid = active[0]['field']['id']
# 4. Fetch
data = fetch_series(sid, last=12)
```

---

## 3. `/dump` — Descarga del catalogo completo

**URL:** `GET https://apis.datos.gob.ar/series/api/dump`

Descarga el catalogo COMPLETO de series (todos los IDs + metadata, sin
datapoints). **Pesado** — varios MB. Solo usar para indexar o sincronizar.

### Parametros

| Param | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| `format` | enum | `json` | `json` o `csv` |

### Ejemplo

```bash
GET /dump?format=csv
```

Devuelve un CSV con cada row = 1 serie con todas sus metadatas.

### Casos de uso

- Construir un indice local de IDs para busqueda offline.
- Auditoria de series nuevas / discontinuadas.
- Bulk processing.

### NO usar para

- Consultas casuales de quote (usar `/series` por ID).
- Busqueda interactiva (usar `/search`).

---

## 4. `/validate` — Validacion de queries

**URL:** `GET https://apis.datos.gob.ar/series/api/validate`

Valida que un ID (o combinacion de params) sea valido SIN ejecutar la
query real. Util para debugging y validacion preventiva.

### Parametros

Mismos que `/series` pero solo se valida la sintaxis.

### Ejemplo

```bash
GET /validate?ids=145.3_INGNACUAL_DICI_M_38
```

Devuelve:

```json
{
  "data": [{...metadata sin datos...}]
}
```

Si el ID es invalido:

```json
{
  "errors": [
    {"error": "El ID 'XXX' no es un identificador de serie valido"}
  ]
}
```

### Casos de uso

- En forms cliente-side validar ID antes de submit.
- Bulk validation antes de un job grande.
- Health check periodico de IDs cacheados.

---

## 5. Decidir que endpoint usar

| Escenario | Endpoint |
|-----------|----------|
| Conozco el ID y quiero datos | `/series` |
| No conozco el ID, busco por keyword | `/search` |
| Quiero validar un ID antes de fetch | `/validate` |
| Necesito sincronizar todo el catalogo offline | `/dump` |
| Quiero descargar datos en CSV para Excel | `/series?format=csv` |

### Workflow tipico

```
search(q) → validate(id) → series(ids)
```

1. **Discovery:** `search()` para encontrar IDs candidatos.
2. **Validation (opcional):** `validate()` si vas a cachear el ID.
3. **Fetch:** `series()` para obtener los datos reales.

### Workflow con el script

```bash
# 1. Buscar
py scripts/fetch_indec.py search "pobreza" --limit 5

# 2. Validar el ID elegido
py scripts/fetch_indec.py validate "150.1_LA_POBREZA_0_D_13"

# 3. Fetch
py scripts/fetch_indec.py series "150.1_LA_POBREZA_0_D_13" --last 24
```
