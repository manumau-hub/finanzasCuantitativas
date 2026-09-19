# REPRESENTATION MODES — Las 7 transformaciones builtin

> El parametro `representation_mode` permite que la API **transforme los
> valores raw ANTES de devolverlos**, eliminando la necesidad de calculos
> cliente-side. Es uno de los killer features de esta API.

---

## Indice

1. [Para que sirve](#1-para-que-sirve)
2. [Los 7 modes explicados](#2-los-7-modes-explicados)
3. [Caso de uso: inflacion en todas sus formas](#3-caso-de-uso-inflacion-en-todas-sus-formas)
4. [Tabla comparativa con ejemplos calculados](#4-tabla-comparativa-con-ejemplos-calculados)
5. [Que cambia en el response](#5-que-cambia-en-el-response)
6. [Errores comunes](#6-errores-comunes)

---

## 1. Para que sirve

Cuando trabajamos con series temporales, muy frecuentemente necesitamos
**no el valor raw sino una transformacion** del mismo. Por ejemplo, para
inflacion:

- IPC indice raw → `value` (default)
- Inflacion mensual % → `percent_change`
- Inflacion interanual (YoY) % → `percent_change_a_year_ago`
- Inflacion acumulada del año (YTD) % → `percent_change_since_beginning_of_year`

Sin este parametro, tendrias que **calcular vos** estas variaciones cliente-side
(con riesgo de errores de formula, rounding, etc.). La API las calcula
server-side con la formula correcta.

---

## 2. Los 7 modes explicados

### `value` (default)

**Valor original de la serie tal cual esta publicado.**

```bash
?ids=<ID>&representation_mode=value
```

Equivalente a no pasar el parametro.

### `change`

**Diferencia absoluta entre valor actual y periodo anterior** (mes/trim/año
segun la frecuencia de la serie).

Formula: `change[T] = value[T] - value[T-1]`

```bash
?ids=<ID>&representation_mode=change
```

**Ejemplo con IPC indice** (valor[T-1]=102.4, valor[T]=104.7):
- `value`: 104.7
- `change`: 2.3

Util para series en **unidades absolutas** (cantidades, montos, precios sin
calcular como %).

### `percent_change`

**Variacion porcentual periodo a periodo** (en formato decimal: `0.024` = 2.4%).

Formula: `pct_change[T] = (value[T] - value[T-1]) / value[T-1]`

```bash
?ids=<ID>&representation_mode=percent_change
```

**Ejemplo IPC indice:**
- `value`: 104.7
- `percent_change`: 0.0225 (= +2.25% mensual = **inflacion mensual**)

### `change_a_year_ago`

**Diferencia absoluta vs el mismo periodo del año anterior** (YoY).

Formula: `change_yoy[T] = value[T] - value[T-12meses]`

```bash
?ids=<ID>&representation_mode=change_a_year_ago
```

**Ejemplo:** si valor en mayo 2024 fue 80 y mayo 2025 es 110, devuelve 30.

### `percent_change_a_year_ago`

**Variacion porcentual interanual (YoY).**

Formula: `pct_yoy[T] = (value[T] - value[T-12meses]) / value[T-12meses]`

```bash
?ids=<ID>&representation_mode=percent_change_a_year_ago
```

**ESTO ES INFLACION INTERANUAL** cuando se aplica a un IPC indice.

**Ejemplo:**
- IPC mayo 2024: 100
- IPC mayo 2025: 280
- `percent_change_a_year_ago` en mayo 2025: 1.8 (= **180% YoY**)

### `change_since_beginning_of_year`

**Diferencia absoluta acumulada desde el inicio del año.**

Formula: `change_ytd[T] = value[T] - value[diciembre_año_anterior]`

```bash
?ids=<ID>&representation_mode=change_since_beginning_of_year
```

### `percent_change_since_beginning_of_year`

**Variacion porcentual acumulada YTD.**

Formula: `pct_ytd[T] = (value[T] - value[dic_anterior]) / value[dic_anterior]`

```bash
?ids=<ID>&representation_mode=percent_change_since_beginning_of_year
```

**ESTO ES INFLACION ACUMULADA DEL AÑO** cuando se aplica a un IPC indice.

**Ejemplo:**
- IPC dic 2024: 100
- IPC mayo 2025: 140
- `percent_change_since_beginning_of_year` en mayo 2025: 0.4 (= **40% YTD**)

---

## 3. Caso de uso: inflacion en todas sus formas

Suponiendo que tenemos un ID de IPC indice (nivel general nacional). Una
SOLA serie devuelve **4 formas distintas de inflacion** segun el `mode`:

| Mode | Que devuelve | Lectura |
|------|--------------|---------|
| `value` | Indice raw (base dic 2016 = 100) | "El indice esta en 8,450 pts" |
| `percent_change` | Variacion intermensual % | "Inflacion mensual = 2.6%" |
| `percent_change_a_year_ago` | Variacion interanual % | "Inflacion anual = 35.8%" |
| `percent_change_since_beginning_of_year` | Variacion acumulada YTD | "Inflacion acumulada año = 15.2%" |

### Ejemplo: dashboard de inflacion en 1 sola request por mode

```python
from fetch_indec import fetch_series

ID = "<ID_IPC_INDICE_NIVEL_GENERAL>"

# 1 fetch por cada mode (4 requests totales)
inflacion = {
    "indice": fetch_series(ID, last=12, representation_mode="value"),
    "mensual_pct": fetch_series(ID, last=12, representation_mode="percent_change"),
    "interanual_pct": fetch_series(ID, last=12, representation_mode="percent_change_a_year_ago"),
    "acumulado_ytd_pct": fetch_series(ID, last=12, representation_mode="percent_change_since_beginning_of_year"),
}

# Imprimir tabla
for fecha, valor in zip(...):
    print(f"{fecha}  indice={ind}  mensual={m:.1%}  YoY={y:.1%}  YTD={t:.1%}")
```

---

## 4. Tabla comparativa con ejemplos calculados

Asumimos un IPC indice con estos valores ficticios (mensual):

| Fecha | Indice raw |
|-------|------------|
| 2024-12 | 100.0 |
| 2025-01 | 102.5 |
| 2025-02 | 105.7 |
| 2025-03 | 109.0 |
| 2025-04 | 113.2 |
| 2025-05 | 117.8 |

Para **mayo 2025**:

| Mode | Formula | Resultado |
|------|---------|-----------|
| `value` | `117.8` | **117.8** |
| `change` | `117.8 - 113.2` | **4.6** |
| `percent_change` | `(117.8 - 113.2) / 113.2` | **0.0406** (= 4.06% mensual) |
| `change_a_year_ago` | `117.8 - valor_may_2024` (asumamos 75) | **42.8** |
| `percent_change_a_year_ago` | `(117.8 - 75) / 75` | **0.5707** (= 57.07% YoY) |
| `change_since_beginning_of_year` | `117.8 - 100.0` | **17.8** |
| `percent_change_since_beginning_of_year` | `(117.8 - 100.0) / 100.0` | **0.178** (= 17.8% YTD) |

---

## 5. Que cambia en el response

El campo `meta[1].field` refleja el modo aplicado:

### Con `value` (default)

```json
"field": {
  "id": "...",
  "description": "IPC...",
  "units": "Indice diciembre 2016=100",
  "representation_mode": "value",
  "representation_mode_units": "Indice diciembre 2016=100"
}
```

### Con `percent_change_a_year_ago`

```json
"field": {
  "id": "...",
  "description": "IPC... (variacion interanual)",
  "units": "Indice diciembre 2016=100",
  "representation_mode": "percent_change_a_year_ago",
  "representation_mode_units": "Variacion porcentual interanual"
}
```

Notar que **`units` mantiene la unidad original** pero
`representation_mode_units` te dice la unidad de los valores devueltos.

---

## 6. Errores comunes

### Mode inexistente

```bash
?ids=...&representation_mode=invalid_mode
```

Retorna:

```json
{
  "errors": [
    {"error": "Modo de representacion 'invalid_mode' no es valido"}
  ]
}
```

### Mode aplicado a serie ya transformada

Si la serie YA es una variacion (ej: `145.3_INGNACUAL_DICI_M_38` es la
variacion mensual del IPC), aplicar `representation_mode=percent_change`
calcula "var % de la var %" — generalmente NO es lo que queres.

**Regla:** aplicar transformaciones solo a series tipo INDICE, NO a series
que ya son tasas de variacion.

### Mode YoY al inicio de la serie

`percent_change_a_year_ago` requiere 12 meses de historia. Si pedis los
primeros 12 datapoints de una serie, los primeros valores devueltos van
a ser `null`:

```json
"data": [
  ["2017-01-01", null],
  ["2017-02-01", null],
  ...
  ["2018-01-01", 0.235]
]
```

### Mode YTD en enero

`percent_change_since_beginning_of_year` en enero compara con el valor
de diciembre del año anterior. Si la serie empieza en enero, retorna
`null` para enero.
