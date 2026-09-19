# COOKBOOK — Recetas listas para copy-paste

> 30+ recetas para los casos de uso mas comunes del skill `indec`. Cada
> receta usa el CLI `fetch_indec.py` o la API directa Python.

---

## Indice

### Quote y consulta basica
1. [IPC mensual ultimos 12 meses](#1-ipc-mensual-ultimos-12-meses)
2. [IPC con todas las categorias](#2-ipc-con-todas-las-categorias)
3. [EMAE original + desestacionalizado lado a lado](#3-emae-original--desestacionalizado-lado-a-lado)
4. [RIPTE actual](#4-ripte-actual)
5. [Salario minimo vital y movil](#5-salario-minimo-vital-y-movil)
6. [Snapshot macro Argentina](#6-snapshot-macro-argentina)

### Busqueda y descubrimiento
7. [Buscar serie por keyword](#7-buscar-serie-por-keyword)
8. [Filtrar series activas (sin discontinuadas)](#8-filtrar-series-activas-sin-discontinuadas)
9. [Validar un ID antes de cachearlo](#9-validar-un-id-antes-de-cachearlo)
10. [Inspeccionar metadata sin descargar datos](#10-inspeccionar-metadata-sin-descargar-datos)

### Transformaciones
11. [Inflacion mensual (var %)](#11-inflacion-mensual-var-)
12. [Inflacion interanual YoY](#12-inflacion-interanual-yoy)
13. [Inflacion acumulada YTD](#13-inflacion-acumulada-ytd)
14. [Las 4 formas de inflacion en un dashboard](#14-las-4-formas-de-inflacion-en-un-dashboard)

### Agregacion temporal
15. [Dolar diario → promedio mensual](#15-dolar-diario--promedio-mensual)
16. [Dolar diario → cierre mensual](#16-dolar-diario--cierre-mensual)
17. [Exportaciones mensuales → total anual](#17-exportaciones-mensuales--total-anual)
18. [Reservas mensuales → cierre anual](#18-reservas-mensuales--cierre-anual)

### Comercio exterior
19. [Exportaciones totales por frecuencia](#19-exportaciones-totales-por-frecuencia)

### Empleo y pobreza
20. [Tasa de desempleo nacional](#20-tasa-de-desempleo-nacional)
21. [Linea de pobreza historica](#21-linea-de-pobreza-historica)

### Multi-serie y comparativas
22. [IPC + Salarios + Dolar (poder adquisitivo)](#22-ipc--salarios--dolar-poder-adquisitivo)
23. [Comparar EMAE + IPI + ISAC (actividad economica)](#23-comparar-emae--ipi--isac-actividad-economica)
24. [Reservas vs deuda](#24-reservas-vs-deuda)

### Pipelines y workflows
25. [Pipeline search → validate → fetch](#25-pipeline-search--validate--fetch)
26. [Descargar serie larga (>1000 datapoints)](#26-descargar-serie-larga-1000-datapoints)
27. [Cache local de series](#27-cache-local-de-series)
28. [Exportar a CSV / Pandas](#28-exportar-a-csv--pandas)

### Casos avanzados
29. [Combinar transformacion + agregacion](#29-combinar-transformacion--agregacion)
30. [Calcular inflacion real (deflactar series en pesos)](#30-calcular-inflacion-real-deflactar-series-en-pesos)
31. [Dashboard macro Argentina (todo-en-uno)](#31-dashboard-macro-argentina-todo-en-uno)

---

## 1. IPC mensual ultimos 12 meses

```bash
py scripts/fetch_indec.py ipc --last 12 -q
```

```python
from fetch_indec import ipc

data = ipc(last=12)
for d in data['series'][0]['data']:
    print(f"{d['date']}  {d['value']:.2%}")
```

---

## 2. IPC con todas las categorias

```bash
py scripts/fetch_indec.py ipc-completo --last 6 -q
```

```python
from fetch_indec import ipc_completo
data = ipc_completo(last=6)
print(f"Series devueltas: {data['n_series']}")
for s in data['series']:
    print(f"  {s['description'][:60]}")
```

---

## 3. EMAE original + desestacionalizado lado a lado

```bash
py scripts/fetch_indec.py emae --last 12 -q
```

```python
from fetch_indec import emae
data = emae(last=12)
serie_orig = data['series'][0]
serie_dese = data['series'][1]
print(f"{'Fecha':12} {'Original':>10} {'Desestac':>10}")
for orig, dese in zip(serie_orig['data'], serie_dese['data']):
    print(f"{orig['date']:12} {orig['value']:>10.2f} {dese['value']:>10.2f}")
```

---

## 4. RIPTE actual

```bash
py scripts/fetch_indec.py series "158.1_REPTE_0_0_5" --last 6 -q
```

```python
from fetch_indec import fetch_series
d = fetch_series("158.1_REPTE_0_0_5", last=6)
for x in d['series'][0]['data']:
    print(f"{x['date']}  ARS {x['value']:,.0f}")
```

---

## 5. Salario minimo vital y movil

```bash
py scripts/fetch_indec.py series "57.1_SMVMM_0_M_34" --last 12 -q
```

```python
d = fetch_series("57.1_SMVMM_0_M_34", last=12)
# Ver evolucion del SMVM en los ultimos 12 meses
```

---

## 6. Snapshot macro Argentina

```bash
py scripts/fetch_indec.py snapshot --last 3 -q
```

Devuelve en una sola request: IPC + EMAE desestacionalizado + RIPTE +
dolar + reservas — todo de los ultimos 3 periodos.

```python
from fetch_indec import snapshot
data = snapshot(last=3)
for s in data['series']:
    print(f"\n{s['description'][:70]}")
    for d in s['data']:
        print(f"  {d['date']}  {d['value']}")
```

---

## 7. Buscar serie por keyword

```bash
py scripts/fetch_indec.py search "deuda publica" --limit 10
py scripts/fetch_indec.py search "pobreza"
py scripts/fetch_indec.py search "consumo electricidad"
```

```python
from fetch_indec import search_series

results = search_series("ipc nacional", limit=20)
print(f"Total disponibles: {results['meta'].get('available', '?')}")
for item in results['data']:
    print(f"  {item['field']['id']:42s} - {item['field']['description'][:60]}")
```

---

## 8. Filtrar series activas (sin discontinuadas)

```python
results = search_series("ipc", limit=50)
active = [
    r for r in results['data']
    if 'DISCONTI' not in r['dataset']['title'].upper()
]
print(f"De {len(results['data'])} resultados, {len(active)} estan activos")
```

---

## 9. Validar un ID antes de cachearlo

```bash
py scripts/fetch_indec.py validate "145.3_INGNACUAL_DICI_M_38"
```

```python
from fetch_indec import validate_ids
try:
    r = validate_ids("145.3_INGNACUAL_DICI_M_38")
    print("ID valido")
except Exception as e:
    print(f"ID invalido: {e}")
```

---

## 10. Inspeccionar metadata sin descargar datos

```bash
py scripts/fetch_indec.py series "145.3_INGNACUAL_DICI_M_38" --metadata only
```

Devuelve solo `meta` (sin `data`). Util para saber unidades, source,
frecuencia antes de descargar.

---

## 11. Inflacion mensual (var %)

```bash
# Esta serie YA es la variacion mensual:
py scripts/fetch_indec.py ipc --last 6 -q
```

O desde el indice (si tenes el ID del indice raw):

```bash
py scripts/fetch_indec.py series "<ID_IPC_INDICE>" --mode percent_change --last 6
```

---

## 12. Inflacion interanual YoY

```bash
py scripts/fetch_indec.py series "<ID_IPC_INDICE>" --mode percent_change_a_year_ago --last 12
```

Devuelve la **inflacion anual** ya calculada (ej: 0.45 = 45% YoY).

---

## 13. Inflacion acumulada YTD

```bash
py scripts/fetch_indec.py series "<ID_IPC_INDICE>" --mode percent_change_since_beginning_of_year --last 12
```

Devuelve la **inflacion acumulada del año** a la fecha de cada datapoint.

---

## 14. Las 4 formas de inflacion en un dashboard

```python
from fetch_indec import fetch_series

ID_INDICE = "<ID_IPC_INDICE_NIVEL_GENERAL>"  # buscar con search

inflaciones = {
    "indice": fetch_series(ID_INDICE, last=12, representation_mode="value"),
    "mensual_pct": fetch_series(ID_INDICE, last=12, representation_mode="percent_change"),
    "interanual_pct": fetch_series(ID_INDICE, last=12, representation_mode="percent_change_a_year_ago"),
    "ytd_pct": fetch_series(ID_INDICE, last=12, representation_mode="percent_change_since_beginning_of_year"),
}

# Imprimir tabla
print(f"{'Fecha':12} {'Indice':>8} {'Mensual':>10} {'YoY':>10} {'YTD':>10}")
data_dates = [d['date'] for d in inflaciones['indice']['series'][0]['data']]
for i, fecha in enumerate(data_dates):
    indice = inflaciones['indice']['series'][0]['data'][i]['value']
    m = inflaciones['mensual_pct']['series'][0]['data'][i]['value']
    y = inflaciones['interanual_pct']['series'][0]['data'][i]['value']
    t = inflaciones['ytd_pct']['series'][0]['data'][i]['value']
    print(f"{fecha:12} {indice:>8.1f} {m or 0:>10.2%} {y or 0:>10.2%} {t or 0:>10.2%}")
```

---

## 15. Dolar diario → promedio mensual

```bash
py scripts/fetch_indec.py series "168.1_T_CAMBIOR_D_0_0_26" --collapse month --aggregation avg --last 12
```

```python
data = fetch_series(
    "168.1_T_CAMBIOR_D_0_0_26",
    collapse="month", collapse_aggregation="avg",
    last=12,
)
```

---

## 16. Dolar diario → cierre mensual

```bash
py scripts/fetch_indec.py series "168.1_T_CAMBIOR_D_0_0_26" --collapse month --aggregation end_of_period --last 12
```

Devuelve el dolar del ultimo dia habil de cada mes (util para reportes
contables).

---

## 17. Exportaciones mensuales → total anual

```bash
py scripts/fetch_indec.py series "75.3_IETG_0_M_31" --collapse year --aggregation sum --last 10
```

---

## 18. Reservas mensuales → cierre anual

```bash
py scripts/fetch_indec.py series "92.1_RID_0_0_32" --collapse year --aggregation end_of_period --last 10
```

Devuelve el saldo de reservas al cierre de cada año.

---

## 19. Exportaciones totales por frecuencia

```bash
py scripts/fetch_indec.py comercio --last 12 -q
```

Devuelve exportaciones totales mensual + trimestral + anual en un dict.

```python
from fetch_indec import comercio
data = comercio(last=12)
for s in data['series']:
    print(f"\n{s['description']}")
    print(f"  Frecuencia inferida: {s.get('units')}")
    for d in s['data'][-3:]:
        print(f"  {d['date']}  USD {d['value']:,.0f}M")
```

---

## 20. Tasa de desempleo nacional

```bash
py scripts/fetch_indec.py series "42.3_EPH_PUNTUATAL_0_M_30" --last 8 -q
```

```python
data = fetch_series("42.3_EPH_PUNTUATAL_0_M_30", last=8)
for d in data['series'][0]['data']:
    print(f"{d['date']}  {d['value']:.1f}%")
```

---

## 21. Linea de pobreza historica

```bash
py scripts/fetch_indec.py series "150.1_LA_POBREZA_0_D_13" --last 24 -q
```

Devuelve la linea de pobreza en pesos corrientes para los ultimos 24 meses.

---

## 22. IPC + Salarios + Dolar (poder adquisitivo)

```python
from fetch_indec import fetch_series

# Multi-serie en 1 request
data = fetch_series(
    "145.3_INGNACUAL_DICI_M_38,158.1_REPTE_0_0_5,168.1_T_CAMBIOR_D_0_0_26",
    last=12,
)

# Tomar las 3 series
ipc_var, ripte, dolar = data['series']
print(f"{'Fecha':12} {'IPC%':>8} {'RIPTE':>12} {'Dolar':>10}")
for i in range(len(ipc_var['data'])):
    fecha = ipc_var['data'][i]['date']
    ipc_val = ipc_var['data'][i]['value']
    ripte_val = ripte['data'][i]['value']
    dolar_val = dolar['data'][i]['value']
    print(f"{fecha:12} {ipc_val:>8.2%} {ripte_val:>12,.0f} {dolar_val:>10,.0f}")
```

---

## 23. Comparar EMAE + IPI + ISAC (actividad economica)

```python
data = fetch_series(
    "143.3_NO_PR_2004_A_31,453.1_SERIE_ORIGNAL_0_0_14_46,33.2_ISAC_NIVELRAL_0_M_18_63",
    last=12,
)
# 3 indicadores de actividad lado a lado
```

---

## 24. Reservas vs deuda

```python
# Buscar deuda publica primero
from fetch_indec import search_series
search_series("deuda publica nacional")

# Combinar con reservas
data = fetch_series("92.1_RID_0_0_32,<ID_DEUDA>", last=24)
```

---

## 25. Pipeline search → validate → fetch

```python
from fetch_indec import search_series, validate_ids, fetch_series

# 1. Buscar
results = search_series("ipc nucleo nacional", limit=10)
candidates = [
    r for r in results['data']
    if 'DISCONTI' not in r['dataset']['title'].upper()
]
chosen_id = candidates[0]['field']['id']
print(f"Elegido: {chosen_id}")

# 2. Validar
validate_ids(chosen_id)

# 3. Fetch
data = fetch_series(chosen_id, last=12)
```

---

## 26. Descargar serie larga (>1000 datapoints)

```python
def fetch_full(series_id, **kwargs):
    """Pagina automaticamente para descargar TODA una serie."""
    all_data = []
    offset = 0
    LIMIT = 1000
    while True:
        chunk_resp = fetch_series(series_id, limit=LIMIT, start=offset, **kwargs)
        chunk = chunk_resp['series'][0]['data']
        if not chunk:
            break
        all_data.extend(chunk)
        if len(chunk) < LIMIT:
            break
        offset += LIMIT
    return all_data

# Descargar dolar diario completo (varios miles de datapoints)
todo = fetch_full("168.1_T_CAMBIOR_D_0_0_26")
print(f"Total datapoints: {len(todo)}")
```

---

## 27. Cache local de series

```python
import json
import time
from pathlib import Path
from fetch_indec import fetch_series

CACHE = Path("./indec_cache")
CACHE.mkdir(exist_ok=True)

def fetch_cached(series_id, ttl_hours=24, **kwargs):
    """Wrapper que cachea responses por TTL."""
    fp = CACHE / f"{series_id.replace('.','_')}.json"
    if fp.exists() and (time.time() - fp.stat().st_mtime) / 3600 < ttl_hours:
        return json.loads(fp.read_text(encoding='utf-8'))
    data = fetch_series(series_id, **kwargs)
    fp.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return data

# Uso
data = fetch_cached("145.3_INGNACUAL_DICI_M_38", ttl_hours=12, last=12)
```

---

## 28. Exportar a CSV / Pandas

```python
import pandas as pd

# Opcion A: pedir CSV directo desde la API
df = pd.read_csv(
    "https://apis.datos.gob.ar/series/api/series?ids=145.3_INGNACUAL_DICI_M_38&format=csv&limit=1000",
    parse_dates=['indice_tiempo']
)

# Opcion B: convertir JSON normalizado a DataFrame
from fetch_indec import fetch_series
data = fetch_series("145.3_INGNACUAL_DICI_M_38", last=24)
df = pd.DataFrame(data['series'][0]['data'])
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')
print(df)
```

---

## 29. Combinar transformacion + agregacion

```bash
# Inflacion YoY del IPC indice + agregar a anual
py scripts/fetch_indec.py series "<ID_IPC_INDICE>" \
   --mode percent_change_a_year_ago \
   --collapse year --aggregation avg \
   --last 10
```

Devuelve la inflacion YoY promedio por año (un dato por año).

---

## 30. Calcular inflacion real (deflactar series en pesos)

```python
# RIPTE en pesos corrientes
ripte = fetch_series("158.1_REPTE_0_0_5", last=120)
# IPC indice nivel general (necesitamos IPC indice raw, no var %)
ipc = fetch_series("<ID_IPC_INDICE_NIVEL_GENERAL>", last=120)

# Deflactar
ripte_real = []
for r, i in zip(ripte['series'][0]['data'], ipc['series'][0]['data']):
    if r['value'] and i['value']:
        # Pesos constantes base del IPC (ej: base dic 2016 = 100)
        ripte_real.append({
            'date': r['date'],
            'pesos_corrientes': r['value'],
            'pesos_constantes': r['value'] / i['value'] * 100,
        })

# Imprimir
for x in ripte_real[-12:]:
    print(f"{x['date']}  corrientes={x['pesos_corrientes']:>12,.0f}  constantes={x['pesos_constantes']:>10,.2f}")
```

---

## 31. Dashboard macro Argentina (todo-en-uno)

```bash
py scripts/fetch_indec.py all --last 6 -o macro_snapshot.json
```

Combina **IPC + EMAE + salarios + dolar + reservas + construccion + comercio**
en una request (con sleep entre cada una). Output guardado a archivo.

```python
from fetch_indec import fetch_all
data = fetch_all(last=12)

print("=== DASHBOARD MACRO ARGENTINA ===\n")
for indicator in ['ipc', 'emae', 'dolar', 'reservas']:
    section = data[indicator]
    if 'error' in section:
        continue
    serie = section['series'][0]
    last_value = serie['data'][-1]
    print(f"{indicator.upper():12} {serie['description'][:50]:50}  {last_value['date']}  {last_value['value']}")
```
