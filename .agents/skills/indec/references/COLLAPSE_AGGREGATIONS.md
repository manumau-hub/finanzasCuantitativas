# COLLAPSE AGGREGATIONS — Agregacion temporal

> Los parametros `collapse` + `collapse_aggregation` permiten **convertir
> una serie de mayor frecuencia a una de menor frecuencia** (ej: diaria
> → mensual, mensual → anual) DIRECTAMENTE en el server, sin procesar
> cliente-side.

---

## Indice

1. [Para que sirve](#1-para-que-sirve)
2. [Valores validos de `collapse`](#2-valores-validos-de-collapse)
3. [Valores validos de `collapse_aggregation`](#3-valores-validos-de-collapse_aggregation)
4. [Cuando usar cada `aggregation`](#4-cuando-usar-cada-aggregation)
5. [Casos de uso comunes](#5-casos-de-uso-comunes)
6. [Combinaciones con representation_mode](#6-combinaciones-con-representation_mode)
7. [Reglas y restricciones](#7-reglas-y-restricciones)
8. [Errores comunes](#8-errores-comunes)

---

## 1. Para que sirve

Convertir serie diaria a mensual o anual (downsample) es muy comun en
analisis macro. Sin esta funcionalidad, tendrias que:

1. Descargar TODOS los datapoints diarios (paginando).
2. Hacer un groupby por mes/año en pandas.
3. Aplicar agregacion adecuada (avg, sum, ...).

Con `collapse` + `collapse_aggregation`, en **una sola llamada** la API
te devuelve la serie ya agregada.

### Beneficios

- ✅ **Menos datos transferidos** (4 datapoints anuales en lugar de 1000+ diarios).
- ✅ **Menos requests** (no hay que paginar).
- ✅ **Aggregation correcta** (la API sabe que "promedio" de tipo de cambio
  o "suma" de exportaciones es lo apropiado).
- ✅ **Sincronizacion con metadata** (units, descripcion se ajustan).

---

## 2. Valores validos de `collapse`

| Valor | Frecuencia resultado | Comentario |
|-------|---------------------|------------|
| `day` | Diaria | Solo util si serie original es sub-diaria (raro). |
| `week` | Semanal | Convierte daily → weekly. |
| `month` | Mensual | El mas usado: convierte daily → monthly. |
| `quarter` | Trimestral | Convierte monthly → quarterly. |
| `semester` | Semestral | Convierte monthly/quarterly → semestral. |
| `year` | Anual | Convierte cualquier frecuencia menor → anual. |

### Ejemplos

```bash
?ids=<DOLAR_DIARIO>&collapse=month        # diario → mensual
?ids=<DOLAR_DIARIO>&collapse=quarter      # diario → trimestral
?ids=<DOLAR_DIARIO>&collapse=year         # diario → anual
?ids=<IPC_MENSUAL>&collapse=quarter       # mensual → trimestral
?ids=<EXPORTACIONES_MENSUAL>&collapse=year # mensual → anual
```

---

## 3. Valores validos de `collapse_aggregation`

**Default:** `avg`. Solo aplica cuando `collapse` esta presente.

| Valor | Que hace | Ejemplo |
|-------|----------|---------|
| `avg` | Promedio del periodo | Dolar mensual = avg(dolar diario del mes) |
| `sum` | Suma del periodo | Exportaciones anuales = sum(exportaciones mensuales del año) |
| `end_of_period` | Valor del ultimo periodo dentro del nuevo | Dolar mensual = dolar del ultimo dia habil del mes |
| `min` | Minimo del periodo | Tasa minima del mes |
| `max` | Maximo del periodo | Pico maximo |

---

## 4. Cuando usar cada `aggregation`

La eleccion correcta depende de **que mide la serie**:

### Series de FLOW (volumenes, transacciones) → `sum`

Cosas que se suman a lo largo del periodo:
- Exportaciones / importaciones
- Volumen de transacciones bursatiles
- Recaudacion tributaria
- Subsidios pagados
- Personas ocupadas/contratadas

```bash
?ids=75.3_IETG_0_M_31&collapse=year&collapse_aggregation=sum
# Exportaciones mensuales → total anual
```

### Series de PRICE / RATE / INDEX → `avg`

Cosas donde el "promedio del periodo" tiene sentido:
- Tipo de cambio diario → mensual promedio
- Tasas de interes
- Indices de precios
- Indices economicos (EMAE, ISAC)
- Ratios

```bash
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=avg
# Dolar diario → promedio mensual (default)
```

### Series de STOCK (saldos, niveles) → `end_of_period`

Cosas donde lo que importa es el valor al cierre del periodo:
- Reservas internacionales BCRA
- Saldos de cuentas
- Deuda publica
- Capital social
- M2, M3, base monetaria

```bash
?ids=92.1_RID_0_0_32&collapse=year&collapse_aggregation=end_of_period
# Reservas mensuales → cierre anual (saldo a dic)
```

### Para analisis especial → `min` / `max`

- Minimo / maximo del dolar en el periodo
- Volatilidad

```bash
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=max
# Dolar maximo del mes
```

---

## 5. Casos de uso comunes

### Caso 1: Dolar diario → resumen mensual completo

Para un reporte mensual del dolar, necesitas avg + min + max + cierre.

```python
ID = "168.1_T_CAMBIOR_D_0_0_26"
calls = {
    "avg": fetch_series(ID, collapse="month", collapse_aggregation="avg"),
    "min": fetch_series(ID, collapse="month", collapse_aggregation="min"),
    "max": fetch_series(ID, collapse="month", collapse_aggregation="max"),
    "cierre": fetch_series(ID, collapse="month", collapse_aggregation="end_of_period"),
}
# Imprimir tabla:
# Mes      Avg     Min     Max     Cierre
# Ene-25   850     820     880     875
# Feb-25   890     850     920     915
# ...
```

### Caso 2: Exportaciones mensuales → totales anuales

```bash
?ids=75.3_IETG_0_M_31&collapse=year&collapse_aggregation=sum
```

Devuelve totales exportados por año (en millones USD).

### Caso 3: IPC mensual → IPC trimestral promedio

```bash
?ids=<IPC_INDICE_MENSUAL>&collapse=quarter&collapse_aggregation=avg
```

Util para reportes trimestrales o comparacion con PIB (que es trimestral).

### Caso 4: Reservas mensuales → saldo de fin de año

```bash
?ids=92.1_RID_0_0_32&collapse=year&collapse_aggregation=end_of_period
```

### Caso 5: PIB trimestral → PIB anual (suma de los 4 trimestres)

```bash
?ids=<PIB_TRIMESTRAL>&collapse=year&collapse_aggregation=sum
```

---

## 6. Combinaciones con representation_mode

`collapse` + `representation_mode` son **completamente independientes** y
combinables.

### Ejemplo: dolar diario → cierre mensual → variacion YoY

```bash
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=end_of_period&representation_mode=percent_change_a_year_ago
```

Devuelve: para cada fin de mes, la **devaluacion del peso vs el mismo
mes año anterior**.

### Ejemplo: exportaciones mensuales → suma anual → variacion vs año anterior

```bash
?ids=75.3_IETG_0_M_31&collapse=year&collapse_aggregation=sum&representation_mode=percent_change
```

Devuelve: para cada año, el cambio porcentual del total exportado vs año
anterior.

### Orden de aplicacion

La API aplica:
1. Primero `collapse + collapse_aggregation` (downsample temporal).
2. Despues `representation_mode` (transformacion sobre los valores agregados).

---

## 7. Reglas y restricciones

### Regla 1: solo downsample, no upsample

`collapse` solo puede agregar de **mayor a menor frecuencia**:

- ✅ daily → monthly
- ✅ monthly → quarterly
- ❌ monthly → daily (retorna error 400)
- ❌ quarterly → monthly (retorna error 400)

### Regla 2: orden de frecuencias

De mayor a menor frecuencia:

```
day > week > month > quarter > semester > year
```

### Regla 3: aggregation requiere collapse

`collapse_aggregation=sum` sin `collapse` es ignorado silenciosamente.

### Regla 4: default es avg

Si pasas `collapse=month` sin `collapse_aggregation`, asume `avg`.

### Regla 5: collapse no afecta multi-serie de distintas frecuencias

Si en `?ids=A,B` A es mensual y B es trimestral, `collapse=year` agrega
ambas a anual con la misma aggregation.

---

## 8. Errores comunes

### Error: "collapse no puede aumentar la frecuencia"

```bash
?ids=<serie_mensual>&collapse=day
```

Retorna:

```json
{"errors": [{"error": "El parametro collapse 'day' es invalido para una serie de frecuencia 'month'"}]}
```

**Fix:** usar una collapse igual o menor frecuencia que la serie original.

### Aggregation incorrecta semanticamente

```bash
# WRONG: sumar tipos de cambio (no tiene sentido)
?ids=168.1_T_CAMBIOR_D_0_0_26&collapse=month&collapse_aggregation=sum
```

La API te devuelve los datos, **pero el resultado no tiene sentido**.

**Fix:** aprender que aggregation corresponde a cada tipo de serie
(seccion 4 de este doc).

### Combinar `collapse` con `last`

```bash
?ids=...&collapse=year&last=5
```

Esto SI es valido y muy util: agrega + devuelve los ultimos N periodos
agregados. Ej: ultimos 5 años de exportaciones totales.
