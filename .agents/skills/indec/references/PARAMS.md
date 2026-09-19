# PARAMS — Referencia exhaustiva de parametros

> Cada parametro del endpoint `/series` explicado en detalle con valores
> validos, defaults, ejemplos y caveats.

---

## Indice

1. [`ids` — Series a fetchear](#1-ids--series-a-fetchear)
2. [`format` — JSON vs CSV](#2-format--json-vs-csv)
3. [`start_date`, `end_date` — Filtros temporales](#3-start_date-end_date--filtros-temporales)
4. [`representation_mode` — Transformaciones](#4-representation_mode--transformaciones)
5. [`collapse`, `collapse_aggregation` — Agregacion temporal](#5-collapse-collapse_aggregation--agregacion-temporal)
6. [`limit`, `start` — Paginacion](#6-limit-start--paginacion)
7. [`last` — Ultimos N valores](#7-last--ultimos-n-valores)
8. [`sort` — Orden](#8-sort--orden)
9. [`metadata` — Verbosidad](#9-metadata--verbosidad)
10. [`header` — Headers de CSV](#10-header--headers-de-csv)
11. [Combinaciones validas vs invalidas](#11-combinaciones-validas-vs-invalidas)

---

## 1. `ids` — Series a fetchear

**Requerido. Tipo:** string CSV (IDs separados por coma).

### Sintaxis

```
?ids=ID1
?ids=ID1,ID2,ID3
```

### Ejemplos

```bash
# Una serie
?ids=145.3_INGNACUAL_DICI_M_38

# Multi-serie (combinable hasta multiples IDs)
?ids=145.3_INGNACUAL_DICI_M_38,158.1_REPTE_0_0_5,168.1_T_CAMBIOR_D_0_0_26
```

### Validaciones server-side

- Los IDs deben existir en el catalogo o retorna 404.
- Si UN ID es invalido en un multi-call, retorna 400 con error indicando cual.

### ⚠️ Caveat: frecuencias mezcladas

Si pasas IDs de frecuencias distintas (ej: una mensual + una diaria):

- La API agrega las series usando la frecuencia mas baja (mensual).
- Los datapoints de la serie de mayor frecuencia (diaria) se colapsan
  con `avg` por defecto.
- Para controlar el collapse: usar params `collapse` + `collapse_aggregation`
  explicitos.

### Limite practico

No hay limite documentado, pero recomendado: **max 20-50 IDs** por request
para evitar timeouts. Para descargas masivas usar `/dump`.

---

## 2. `format` — JSON vs CSV

**Default:** `json`. Valores: `json`, `csv`.

### Diferencias

| Aspecto | JSON | CSV |
|---------|------|-----|
| Estructura | Anidado con metadata | Flat tabular |
| Metadata incluido | ✅ en `meta` field | ❌ (solo header) |
| Idoneo para | Codigo / parsing programatico | Excel / Pandas direct read |
| Tamaño | Mayor (overhead JSON) | Menor (mas compacto) |

### Ejemplos

```bash
?ids=145.3_INGNACUAL_DICI_M_38&format=json
```

```json
{"data": [["2026-04-01", 0.0258]], "meta": [...], ...}
```

```bash
?ids=145.3_INGNACUAL_DICI_M_38&format=csv
```

```csv
indice_tiempo,IPC_var_mensual
2026-04-01,0.0258
```

### Pandas read

```python
import pandas as pd
url = "https://apis.datos.gob.ar/series/api/series?ids=145.3_INGNACUAL_DICI_M_38&format=csv"
df = pd.read_csv(url)
```

---

## 3. `start_date`, `end_date` — Filtros temporales

**Formato:** `YYYY-MM-DD`. Ambos opcionales.

### Comportamiento

- `start_date`: incluye datapoints desde esa fecha (inclusive).
- `end_date`: hasta esa fecha (inclusive).
- Si la serie es mensual y pasas `start_date=2024-01-15`, devuelve desde
  enero 2024 (no espera el 15).

### Ejemplos

```bash
# Solo desde
?ids=145.3_INGNACUAL_DICI_M_38&start_date=2024-01-01

# Rango completo
?ids=145.3_INGNACUAL_DICI_M_38&start_date=2020-01-01&end_date=2024-12-31

# Solo hasta (raro)
?ids=145.3_INGNACUAL_DICI_M_38&end_date=2020-12-31
```

### Caveats

- Si `start_date > end_date` retorna 400.
- Si la fecha esta antes del primer datapoint disponible, retorna desde el primero.
- Si esta despues del ultimo, devuelve `data: []`.

---

## 4. `representation_mode` — Transformaciones

**Default:** `value`. Valores:

| Mode | Descripcion corta |
|------|-------------------|
| `value` | Valor raw original |
| `change` | Diff absoluta vs periodo anterior |
| `percent_change` | Var % vs periodo anterior |
| `change_a_year_ago` | Diff absoluta YoY |
| `percent_change_a_year_ago` | Var % YoY (**inflacion interanual**) |
| `change_since_beginning_of_year` | Diff absoluta YTD |
| `percent_change_since_beginning_of_year` | Var % YTD (**inflacion acumulada año**) |

Ver documento dedicado en [REPRESENTATION_MODES.md](./REPRESENTATION_MODES.md)
con ejemplos calculados.

### Ejemplo: inflacion YoY desde el indice IPC nivel general

```bash
# Suponiendo que tenemos el ID del IPC indice (no la var)
?ids=<ID_IPC_INDICE>&representation_mode=percent_change_a_year_ago
```

Devuelve directamente la **inflacion interanual** ya calculada sin
procesamiento cliente-side.

---

## 5. `collapse`, `collapse_aggregation` — Agregacion temporal

Ver documento dedicado en [COLLAPSE_AGGREGATIONS.md](./COLLAPSE_AGGREGATIONS.md)
con casos completos.

### `collapse`

**Default:** none (mantener frecuencia original). Valores:

| Valor | Convierte a |
|-------|-------------|
| `day` | Diaria |
| `week` | Semanal |
| `month` | Mensual |
| `quarter` | Trimestral |
| `semester` | Semestral |
| `year` | Anual |

### `collapse_aggregation`

**Default:** `avg`. Valores:

| Valor | Descripcion |
|-------|-------------|
| `avg` | Promedio |
| `sum` | Suma |
| `end_of_period` | Valor del fin del periodo |
| `min` | Minimo |
| `max` | Maximo |

### Ejemplos

```bash
# Dolar diario → promedio mensual
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=avg

# Dolar diario → cierre mensual (ultimo dia del mes)
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=end_of_period

# Exportaciones mensuales → total anual
?ids=75.3_IETG_0_M_31&collapse=year&collapse_aggregation=sum
```

### Caveats

- `collapse` solo agrega de mayor a menor frecuencia. **No podes
  "desagregar"** mensual a diario (retorna 400).
- Si la serie ya esta en la frecuencia que pediste, `collapse` es no-op.
- `collapse_aggregation` se ignora si no hay `collapse`.

---

## 6. `limit`, `start` — Paginacion

### `limit`

**Default:** 100. **Maximo:** 1,000 (limite server-side, no podes superarlo
ni pidiendo mas).

```bash
?ids=...&limit=1000
```

### `start`

**Default:** 0. Offset (skip los primeros N datapoints).

```bash
?ids=...&limit=1000&start=0     # primeros 1000
?ids=...&limit=1000&start=1000  # siguientes 1000
?ids=...&limit=1000&start=2000  # etc.
```

### Caveats

- ⚠️ `limit` SE IGNORA si pasas `last` (ver seccion 7).
- Para descargas masivas de una sola serie (>1000 datapoints), paginar
  con sucesivos `start`.

### Ejemplo: descargar TODA una serie

```python
all_data = []
offset = 0
LIMIT = 1000
while True:
    r = requests.get(URL, params={"ids": SID, "limit": LIMIT, "start": offset})
    chunk = r.json()['data']
    if not chunk:
        break
    all_data.extend(chunk)
    offset += LIMIT
```

---

## 7. `last` — Ultimos N valores

**Default:** none. Si se pasa, devuelve los ultimos N valores en orden cronologico.

```bash
?ids=145.3_INGNACUAL_DICI_M_38&last=12   # ultimos 12 valores
```

### ⚠️ INCOMPATIBLE con `sort`, `start`, `limit`

Si combinas, retorna **HTTP 400**:

```json
{
  "errors": [
    {"error": "El parametro last no puede ser utilizado junto a sort, start, limit"}
  ]
}
```

El script `fetch_indec.py` maneja esto automaticamente: si pasas `--last`,
no envia `sort/start/limit` al server.

### Por que existe `last`

Es un atajo para el caso comun "quiero los datos mas recientes" sin
tener que calcular el offset. Internamente la API hace `LIMIT N OFFSET (count-N)`.

---

## 8. `sort` — Orden

**Default:** `asc`. Valores: `asc`, `desc`.

```bash
?ids=...&sort=desc   # mas reciente primero
?ids=...&sort=asc    # mas antiguo primero (default)
```

### Caveat

Incompatible con `last` (ver seccion 7).

---

## 9. `metadata` — Verbosidad

**Default:** `full`. Valores:

| Valor | Que incluye |
|-------|-------------|
| `none` | Solo `data` y `count`. Sin metadata. |
| `only` | Solo `meta`, NO incluye `data`. Util para inspeccionar series. |
| `simple` | `data` + metadata reducida (description, units, source, dataset_title). |
| `full` | `data` + metadata COMPLETA (catalog, dataset, distribution, field con todos los campos). |

### Ejemplos

```bash
# Solo datos (response mas chico)
?ids=...&metadata=none

# Solo info (sin data)
?ids=...&metadata=only

# Data + metadata reducida (recomendado para uso normal)
?ids=...&metadata=simple

# Todo (default, mayor tamaño)
?ids=...&metadata=full
```

### Recomendacion

Usar `simple` para uso normal — incluye la info que necesitas (units,
source, description) sin el overhead del `full`.

---

## 10. `header` — Headers de CSV

**Default:** `titles`. Valores: `titles`, `ids`, `descriptions`. Solo aplica
con `format=csv`.

| Valor | Header de columnas |
|-------|--------------------|
| `titles` | Titulos cortos: `indice_tiempo, IPC_var_mensual` |
| `ids` | IDs raw: `indice_tiempo, 145.3_INGNACUAL_DICI_M_38` |
| `descriptions` | Descripciones completas: `indice_tiempo, "IPC. Tasa de variacion mensual..."` |

### Ejemplos

```bash
?ids=...&format=csv&header=ids
```

```csv
indice_tiempo,145.3_INGNACUAL_DICI_M_38
2026-04-01,0.0258
```

vs

```bash
?ids=...&format=csv&header=descriptions
```

```csv
indice_tiempo,IPC. Tasa de variación mensual. Nivel General. Nacional. Base dic 2016.
2026-04-01,0.0258
```

---

## 11. Combinaciones validas vs invalidas

### ✅ Validas (comunes)

```bash
# Quote ultimos 12 meses con metadata reducida
?ids=...&last=12&metadata=simple

# Rango completo con representation
?ids=...&start_date=2024-01-01&end_date=2024-12-31&representation_mode=percent_change_a_year_ago

# Dolar diario → mensual end-of-period
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=end_of_period

# Multi-serie con sort desc
?ids=A,B,C&sort=desc&limit=20

# CSV con header de IDs
?ids=A,B&format=csv&header=ids
```

### ❌ Invalidas (retornan 400)

```bash
# last con sort/start/limit
?ids=...&last=12&sort=desc           # ERROR
?ids=...&last=12&start=0             # ERROR
?ids=...&last=12&limit=20            # ERROR

# collapse a frecuencia mayor que la serie
?ids=<serie_mensual>&collapse=day    # ERROR

# start_date > end_date
?ids=...&start_date=2024-12-31&end_date=2024-01-01   # ERROR

# header con format=json (no es ERROR pero es no-op)
?ids=...&format=json&header=ids      # ignorado
```

### Combinaciones avanzadas

```bash
# Inflacion YoY del IPC indice + collapse a trimestral promedio
?ids=<ID_IPC_INDICE>&representation_mode=percent_change_a_year_ago&collapse=quarter&collapse_aggregation=avg

# Dolar diario → ultimo dia mes → solo ultimos 24 meses
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=end_of_period&last=24
```
