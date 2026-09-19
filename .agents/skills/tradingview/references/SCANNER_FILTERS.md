# Scanner Filters — Sintaxis Completa

> Sintaxis del array `filter` en el payload del Scanner. Permite
> construir queries arbitrarias tipo SQL sobre el universo de ~100k+
> instrumentos en TradingView.

---

## Indice

1. [Anatomia del filter](#1-anatomia-del-filter)
2. [Operaciones soportadas](#2-operaciones-soportadas)
3. [Multiples filtros — AND implicito](#3-multiples-filtros--and-implicito)
4. [Sort](#4-sort)
5. [Pagination via range](#5-pagination-via-range)
6. [Casos comunes](#6-casos-comunes)
7. [Casos avanzados](#7-casos-avanzados)
8. [Errores comunes](#8-errores-comunes)

---

## 1. Anatomia del filter

Cada filtro es un dict con 3 keys:

```json
{
  "left": "<column_name>",
  "operation": "<operation>",
  "right": <value>
}
```

| Key | Tipo | Descripcion |
|-----|------|-------------|
| `left` | str | Nombre de la columna (debe estar en el catalogo del scanner) |
| `operation` | str | Operador (ver tabla abajo) |
| `right` | mixed | Valor o lista de valores (depende del operador) |

Ejemplo:

```json
{"left": "sector", "operation": "equal", "right": "Finance"}
```

---

## 2. Operaciones soportadas

### Igualdad / desigualdad

| Operacion | Tipo `right` | Significado |
|-----------|--------------|-------------|
| `equal` | str/number | `left == right` |
| `nequal` | str/number | `left != right` |

### Comparacion numerica

| Operacion | Tipo `right` | Significado |
|-----------|--------------|-------------|
| `greater` | number | `left > right` |
| `egreater` | number | `left >= right` |
| `less` | number | `left < right` |
| `eless` | number | `left <= right` |

### Rango

| Operacion | Tipo `right` | Significado |
|-----------|--------------|-------------|
| `in_range` | `[min, max]` | `min <= left <= max` |
| `not_in_range` | `[min, max]` | `left < min OR left > max` |

### Set membership

| Operacion | Tipo `right` | Significado |
|-----------|--------------|-------------|
| `in_range_strings` | `["a","b","c"]` | `left in [...]` (para strings) |
| `not_in_range_strings` | `["a","b","c"]` | `left not in [...]` |

### Strings (texto)

| Operacion | Tipo `right` | Significado |
|-----------|--------------|-------------|
| `match` | str | `left LIKE '%right%'` (substring match) |
| `nmatch` | str | `left NOT LIKE '%right%'` |

### Booleanos / null

| Operacion | Tipo `right` | Significado |
|-----------|--------------|-------------|
| `empty` | (sin right) | `left IS NULL` |
| `nempty` | (sin right) | `left IS NOT NULL` |
| `equal` con `right: true/false` | bool | para flags booleanos |

### Cross temporal (raro)

| Operacion | Tipo `right` | Significado |
|-----------|--------------|-------------|
| `crosses` | column o num | `left cruza right` (price action) |
| `crosses_above` | column o num | `left cruza right desde abajo` |
| `crosses_below` | column o num | `left cruza right desde arriba` |
| `above%` | column o num | `left > right * (1 + pct)` |
| `below%` | column o num | `left < right * (1 - pct)` |

---

## 3. Multiples filtros — AND implicito

Pasar varios elementos en `filter` aplica un AND implicito:

```json
{
  "filter": [
    {"left": "sector", "operation": "equal", "right": "Technology"},
    {"left": "market_cap_basic", "operation": "greater", "right": 1000000000000},
    {"left": "country", "operation": "equal", "right": "United States"}
  ]
}
```

Equivalente SQL:

```sql
WHERE sector = 'Technology'
  AND market_cap_basic > 1e12
  AND country = 'United States'
```

### Como hacer OR

Para `OR` usar **operadores plurales**:

```json
{"left": "sector", "operation": "in_range_strings", "right": ["Finance", "Technology"]}
```

Equivalente:

```sql
WHERE sector IN ('Finance', 'Technology')
```

> No hay `OR` arbitrario entre columnas distintas. Solo `IN` dentro de una columna.

---

## 4. Sort

```json
{
  "sort": {
    "sortBy": "<column>",
    "sortOrder": "asc" | "desc"
  }
}
```

Ejemplos:

```json
{"sortBy": "market_cap_basic", "sortOrder": "desc"}     // mas grande primero
{"sortBy": "Perf.YTD", "sortOrder": "desc"}              // mejor performance YTD primero
{"sortBy": "dividend_yield_recent", "sortOrder": "desc"} // mas dividendo primero
```

> Solo se puede ordenar por UNA columna. No hay sort por multiples columnas.

---

## 5. Pagination via range

El Scanner NO usa pagination tradicional con `page`. Usa `range: [start, end]`:

```json
"range": [0, 30]    // primeros 30
"range": [30, 60]   // siguientes 30 (skip primeros 30)
"range": [0, 5000]  // primeros 5000 (limite practico)
```

**Limite empirico:** ~5000 por request sin throttle. Para mas, varios
requests con offsets.

---

## 6. Casos comunes

### Top 10 acciones US por market cap

```json
{
  "filter": [
    {"left": "type", "operation": "equal", "right": "stock"},
    {"left": "country", "operation": "equal", "right": "United States"}
  ],
  "columns": ["name", "description", "market_cap_basic", "close", "change"],
  "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
  "range": [0, 10]
}
```

### Empresas argentinas listadas en NASDAQ/NYSE (ADRs)

```json
{
  "filter": [
    {"left": "country", "operation": "equal", "right": "Argentina"},
    {"left": "exchange", "operation": "in_range_strings", "right": ["NASDAQ", "NYSE"]}
  ],
  "columns": ["name", "description", "exchange", "close", "market_cap_basic"],
  "range": [0, 30]
}
```

### Acciones que reportan earnings esta semana

```json
{
  "filter": [
    {
      "left": "earnings_release_next_date",
      "operation": "in_range",
      "right": [1780000000, 1780604800]
    },
    {"left": "type", "operation": "equal", "right": "stock"}
  ],
  "columns": ["name", "description", "earnings_release_next_date", "market_cap_basic"],
  "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
  "range": [0, 50]
}
```

### Stocks oversold (RSI < 30) con high dividend yield

```json
{
  "filter": [
    {"left": "RSI", "operation": "less", "right": 30},
    {"left": "dividend_yield_recent", "operation": "greater", "right": 0.05},
    {"left": "market_cap_basic", "operation": "greater", "right": 1000000000}
  ],
  "columns": ["name", "close", "RSI", "dividend_yield_recent"],
  "sort": {"sortBy": "dividend_yield_recent", "sortOrder": "desc"},
  "range": [0, 20]
}
```

### Stocks con STRONG_BUY rating tecnico

```json
{
  "filter": [
    {"left": "Recommend.All", "operation": "greater", "right": 0.5},
    {"left": "type", "operation": "equal", "right": "stock"}
  ],
  "columns": ["name", "close", "Recommend.All", "Recommend.MA", "Recommend.Other"],
  "sort": {"sortBy": "Recommend.All", "sortOrder": "desc"},
  "range": [0, 50]
}
```

### Stocks de un industria especifica con buen ROE

```json
{
  "filter": [
    {"left": "industry", "operation": "equal", "right": "Regional Banks"},
    {"left": "return_on_equity", "operation": "greater", "right": 15}
  ],
  "columns": ["name", "country", "return_on_equity", "price_book", "dividend_yield_recent"],
  "sort": {"sortBy": "return_on_equity", "sortOrder": "desc"},
  "range": [0, 20]
}
```

### Cryptos por market cap

```json
{
  "filter": [],
  "columns": ["name", "description", "close", "change", "market_cap_basic"],
  "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
  "range": [0, 20]
}
```

Con `market: "crypto"` (no `global`).

### Bonos argentinos

```json
{
  "filter": [
    {"left": "country", "operation": "equal", "right": "Argentina"}
  ],
  "columns": ["name", "description", "close"],
  "range": [0, 30]
}
```

Con `market: "bonds"`.

---

## 7. Casos avanzados

### Golden cross detector (SMA50 cruzando SMA200 desde abajo)

```json
{
  "filter": [
    {
      "left": "SMA50",
      "operation": "crosses_above",
      "right": "SMA200"
    }
  ],
  "columns": ["name", "close", "SMA50", "SMA200"]
}
```

### Death cross detector

```json
{
  "filter": [
    {
      "left": "SMA50",
      "operation": "crosses_below",
      "right": "SMA200"
    }
  ]
}
```

### Stocks cerca del 52-week high (within 5%)

```json
{
  "filter": [
    {"left": "close", "operation": "above%", "right": "price_52_week_high"},
    {"left": "close", "operation": "egreater", "right": 1}
  ]
}
```

> El operador `above%` con `right` como columna compara `close > price_52_week_high * 0.95`.

### Filtro por cantidad de analistas (consenso fuerte)

```json
{
  "filter": [
    {"left": "number_of_analyst_opinions", "operation": "greater", "right": 15},
    {"left": "recommendation_buy", "operation": "greater", "right": "recommendation_sell"},
    {"left": "price_target_average", "operation": "above%", "right": "close"}
  ]
}
```

---

## 8. Errores comunes

### `data: []` con `totalCount: 0`

- **Causa:** filtro demasiado restrictivo, o columna `right` no existe.
- **Solucion:** sacar filtros uno por uno hasta encontrar el problema.

### HTTP 400 `"Invalid request"`

- **Causa:** sintaxis JSON invalida del filter (ej: falta `"left"`).
- **Solucion:** validar JSON con `python -c 'import json; json.loads(...)'`.

### Column `xxx` no devuelve nada

- **Causa:** la columna no existe o no se llama asi.
- **Solucion:** verificar nombre en `SCANNER_COLUMNS.md`. La nomenclatura
  es estricta — `Recommend.All` ≠ `recommend.all` ≠ `recommend_all`.

### Filter por `right: <columna>` no funciona

- **Causa:** algunos operadores solo aceptan numeros, no columnas como
  argumento derecho. `crosses`, `crosses_above`, `crosses_below`,
  `above%`, `below%` SI aceptan. Los demas (`equal`, `greater`, etc.)
  esperan literales.

### Resultados no ordenados como esperaba

- **Causa:** `sortOrder` typo (ej: `descending` no existe).
- **Solucion:** usar `asc` o `desc` exactamente.

---

## Apendice: Operacion equivalente a UNION/SUBQUERY

El Scanner NO soporta UNION ni subqueries. Para union, hacer multiples
requests y mergear cliente-side:

```python
acciones_us = scanner_scan(filter_=[{"left": "country", "operation": "equal", "right": "United States"}], ...)
acciones_ar = scanner_scan(filter_=[{"left": "country", "operation": "equal", "right": "Argentina"}], ...)
combined = acciones_us["data"] + acciones_ar["data"]
```
