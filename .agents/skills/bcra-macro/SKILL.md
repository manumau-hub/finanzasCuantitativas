---
name: bcra-macro
description: API de Estadísticas Monetarias v4.0 del BCRA con 638 series macroeconómicas (reservas, tipo de cambio, tasas, M1/M2/M3, inflación, CER, UVA).
license: MIT
metadata:
  category: finanzas, api, bcra, macroeconomia
  language: es
  source: https://www.bcra.gob.ar/documentacion-apis/?fileName=estadisticas-monetarias-v4
---

# BCRA Macro — API de Estadísticas Monetarias v4.0

API oficial del BCRA para consultar **variables macroeconómicas nacionales** (no provinciales).  
**Base URL:** `https://api.bcra.gob.ar`  
**Catálogo total:** 1220 series → 638 series nacionales en [./references/VARIABLES.md](./references/VARIABLES.md).

## Endpoints

| # | Endpoint | Uso |
|---|----------|-----|
| 1 | `GET /estadisticas/v4.0/Monetarias` | Catálogo de variables (paginado) |
| 2 | `GET /estadisticas/v4.0/Monetarias/{IdVariable}` | Serie histórica de una variable (paginado) |
| 3 | `GET /estadisticas/v4.0/Metodologia` | Índice de metodologías (paginado) |
| 4 | `GET /estadisticas/v4.0/Metodologia/{IdVariable}` | Ficha metodológica de una variable |

**Autenticación:** no requiere. **CORS:** abierto. **Encoding:** ISO-8859-1 en algunos textos.

---

## 1. Catálogo de variables

```
GET /estadisticas/v4.0/Monetarias
```

Devuelve el listado completo con metadatos (`idVariable`, `descripcion`, `categoria`, `tipoSerie`, `periodicidad`, `unidadExpresion`, `moneda`, `primerFechaInformada`, `ultFechaInformado`, `ultValorInformado`).

### Filtros disponibles (query params)

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `IdVariable` | int | Filtra por ID exacto |
| `Categoria` | string | Búsqueda parcial sin acentos (`"depositos"`, `"prestamos"`) |
| `Periodicidad` | string | `D` diaria, `M` mensual, `T` trimestral |
| `Moneda` | string | `PES`, `DOL`, `ML`, `ME`, `MEyML` |
| `TipoSerie` | string | `Stock`, `Flujo`, `Tasa`, etc. |
| `UnidadExpresion` | string | Texto libre |
| `Limit` | int | Default 1000, **máx 3000** |
| `Offset` | int | Paginación (sumar al salto) |

### Ejemplo mínimo

```python
import requests, pandas as pd
r = requests.get("https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias", params={"Limit": 3000})
df = pd.DataFrame(r.json()["results"])
```

---

## 2. Serie histórica de una variable

```
GET /estadisticas/v4.0/Monetarias/{IdVariable}
```

Devuelve `{idVariable, detalle: [{fecha, valor}]}`.

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `IdVariable` | int (path) | Sí | ID de la variable |
| `Desde` | string | No | `YYYY-MM-DD` |
| `Hasta` | string | No | `YYYY-MM-DD` |
| `Limit` | int | No | Default 1000, **máx 3000** |
| `Offset` | int | No | Paginación |

```python
r = requests.get("https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/1",
                 params={"Desde": "2020-01-01", "Hasta": "2025-12-31"})
df = pd.DataFrame(r.json()["results"][0]["detalle"])
df["fecha"] = pd.to_datetime(df["fecha"])
df = df.set_index("fecha").sort_index()
```

---

## 3. Metodologías

```
GET /estadisticas/v4.0/Metodologia           # índice paginado
GET /estadisticas/v4.0/Metodologia/{idVar}   # ficha completa
```

```python
r = requests.get("https://api.bcra.gob.ar/estadisticas/v4.0/Metodologia/1")
print(r.json()["results"][0]["detalle"])
```

---

## 4. Paginación: cómo superar el límite de 3000 registros

El API devuelve **máximo 3000 filas por llamada** y la serie diaria más larga (Reservas internacionales, ID 1) tiene **~9000 observaciones desde 1996**. Hay dos estrategias.

### Estrategia A — Paginación con `Offset` (la más simple)

Iterar sumando `Offset += Limit` hasta que la respuesta venga vacía.

```python
import requests, pandas as pd

def get_serie(id_variable, limit=3000):
    url = f"https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/{id_variable}"
    offset, partes = 0, []
    while True:
        r = requests.get(url, params={"Limit": limit, "Offset": offset}).json()
        det = r["results"][0]["detalle"]
        if not det:
            break
        partes.append(pd.DataFrame(det))
        offset += limit
    df = pd.concat(partes).drop_duplicates("fecha").sort_values("fecha")
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.set_index("fecha")

reservas = get_serie(1)  # ~9000 observaciones desde 1996
```

### Estrategia B — Chunking por rango de fechas (más rápido en serie larga)

Partir el rango total en ventanas (ej. anual) y pedir cada una con `Desde`/`Hasta`. Es **preferible** cuando la serie tiene >50.000 obs o se quieren datos muy antiguos en simultáneo.

```python
import requests, pandas as pd
from datetime import date

def get_serie_por_chunks(id_variable, desde, hasta, ventana_dias=365):
    url = f"https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/{id_variable}"
    partes, d = [], pd.to_datetime(desde)
    fin = pd.to_datetime(hasta)
    while d <= fin:
        h = min(d + pd.Timedelta(days=ventana_dias - 1), fin)
        r = requests.get(url, params={"Desde": d.strftime("%Y-%m-%d"),
                                       "Hasta": h.strftime("%Y-%m-%d"),
                                       "Limit": 3000}).json()
        partes.append(pd.DataFrame(r["results"][0]["detalle"]))
        d = h + pd.Timedelta(days=1)
    df = pd.concat(partes).drop_duplicates("fecha").sort_values("fecha")
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.set_index("fecha")

base = get_serie_por_chunks(15, "1996-01-01", date.today().isoformat())
```

### Estrategia C — Catálogo paginado (para re-listar todas las variables)

```python
def catalogo_completo(limit=3000):
    url = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias"
    offset, todo = 0, []
    while True:
        r = requests.get(url, params={"Limit": limit, "Offset": offset}).json()
        batch = r["results"]
        todo += batch
        if len(batch) < limit:
            break
        offset += limit
    return pd.DataFrame(todo)
```

### Reglas de oro

- La respuesta **no incluye `total`** → siempre hay que chequear con `len(batch) < limit` o `detalle == []`.
- Hacer **una sola llamada grande** (Limit=3000) es más eficiente que muchas chicas.
- La API no impone rate-limit público pero **ser cortés**: agregar `time.sleep(0.2)` entre llamadas si se itera en masa.

---

## Variables nacionales (IDs más usados)

Listado completo en `VARIABLES.md` (638 series nacionales). Las 30 más consultadas:

| ID | Descripción | Per. |
|----|-------------|------|
| 1 | Reservas internacionales (mill. USD) | D |
| 4 | Tipo de cambio minorista ($/USD) | D |
| 5 | Tipo de cambio mayorista de referencia ($/USD) | D |
| 7 | Tasa BADLAR bancos privados (% TNA) | D |
| 8 | Tasa TM20 bancos privados (% TNA) | D |
| 11 | Tasa BAIBAR (% TNA) | D |
| 12 | Tasa depósitos 30 días (% TNA) | D |
| 13 | Tasa adelantos cta. cte. (% TNA) | D |
| 14 | Tasa préstamos personales (% TNA) | D |
| 15 | Base monetaria (mill. $) | D |
| 16 | Circulación monetaria (mill. $) | D |
| 17 | Billetes y monedas en poder del público (mill. $) | D |
| 18 | Depósitos en entidades financieras (mill. $) | D |
| 19 | Préstamos al sector privado (mill. $) | D |
| 26 | Tasa de política monetaria (% TNA) | D |
| 27 | Variación mensual IPC (%) | M |
| 28 | Variación interanual IPC (%) | M |
| 29 | REM - mediana inflación prox. 12 meses (%) | M |
| 30 | CER (índice, base 2.2.02=1) | D |
| 31 | UVA ($) | D |
| 32 | UVI ($) | D |
| 40 | ICL - Índice Contratos Locación ($) | D |
| 1187 | Banda cambiaria - límite inferior ($/USD) | D |
| 1188 | Banda cambiaria - límite superior ($/USD) | D |
| 1189 | Tasa plazo fijo pesos (% TNA) | D |
| 1197 | Tasa Intereses Moratorios TIM (% TNA) | D |
| 1232 | M1 (mill. $) | D |
| 1233 | M2 (mill. $) | D |
| 1234 | M3 (mill. $) | D |

> **Tip:** el ID cambia con la refactorización del API. Para confirmar el ID actual de una variable usar el endpoint de catálogo.

## Categorías presentes en el catálogo

| Categoría | Cantidad nacional | Descripción |
|-----------|-------------------|-------------|
| Principales Variables | 35 | Indicadores macro headline (tasas, TC, reservas, base, CER, UVA, IPC) |
| Informe Monetario Diario | 33 | Series diarias del IMD (líneas del exterior, M1/M2/M3, créditos BCRA) |
| Series.xlsm | 154 | Factores de variación de la base monetaria y reservas |
| Tasas de interés de depósitos | 10 | Tasas de depósitos desagregadas por moneda y plazo |
| Préstamos por tipo de titular y destino | 74 | Préstamos por destino (hipotecarios, prendarios, personales) |
| Préstamos por tipo de titular | 120 | Préstamos al sector público/privado nacional, por moneda |
| Depósitos por tipo de titular | 212 | Depósitos del sector público/privado nacional, por moneda y plazo |

> **Excluidas (582 series provinciales/municipales):** los IDs 322+ desagregan por provincia (Buenos Aires, Córdoba, Santa Fe, etc.) y los items que mencionan "gobiernos provinciales" o "municipales" sin agregado nacional.

## Códigos de moneda

| Código | Significado |
|--------|-------------|
| `ML` | Moneda local (pesos argentinos) |
| `ME` | Moneda extranjera (dólares) |
| `MEyML` | Agregado moneda local + extranjera |
| `USD` | Dólares (sin conversión) |

## Tipos de serie

`Saldos a fin de mes` · `Saldos` · `Tasa de interés` · `Flujo diario` · `Tipo de cambio` · `Variación` · `Cociente` · `Índice` · `Unidad de cuenta` · `Margen` · `Monto`

---

## Consideraciones técnicas

- **Sin autenticación** — no requiere key ni token.
- **Tope de paginado:** 3000 registros por llamada.
- **Encoding:** las respuestas pueden traer caracteres extendidos (ISO-8859-1) — usar `response.encoding` o `pd.read_json(..., encoding="utf-8")`.
- **Formato fechas:** ISO 8601 (`YYYY-MM-DD`).
- **SLA:** best-effort, sin garantías formales.

## Enlaces útiles

- [Documentación oficial](https://www.bcra.gob.ar/documentacion-apis/?fileName=principales-variables-v4)
- [Catálogo de APIs del BCRA](https://www.bcra.gob.ar/apis-banco-central/)
- [Datos monetarios diarios](https://www.bcra.gob.ar/datos-monetarios-diarios/)
- [Metodologías](https://www.bcra.gob.ar/metodologias-de-las-estadisticas-monetarias-y-financieras/)
- [OpenAPI Spec](https://principales-variables.bcra.apidocs.ar/openapi.json)
- [Docs interactivas](https://principales-variables.bcra.apidocs.ar/)
