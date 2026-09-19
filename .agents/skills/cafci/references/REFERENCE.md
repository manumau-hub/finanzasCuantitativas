# CAFCI — Referencia Completa de la API

> **CAFCI** = Camara Argentina de Fondos Comunes de Inversion. Cobertura
> completa de los **fondos comunes de inversion** argentinos (~1152 fondos,
> ~4615 clases).
>
> Esta documentacion cubre las 4 fuentes publicas que reemplazaron la API
> REST anterior (`api.pub.cafci.org.ar/tipo-renta`, `/fondo/...`,
> `/estadisticas/...`) discontinuada en **2026-04** (HTTP 403 "Route not
> allowed"). No hay API key, no hay autenticacion.

---

## Indice

1. [Resumen de endpoints](#1-resumen-de-endpoints)
2. [Convenciones](#2-convenciones)
3. [Catalogo JSON — `/consulta-de-fondos.json`](#3-catalogo-json--consulta-de-fondosjson)
4. [Snapshot diario XLSX — `/pb_get`](#4-snapshot-diario-xlsx--pb_get)
5. [Ficha individual (Markdown) — defuddle.md](#5-ficha-individual-markdown--defuddlemd)
6. [Composicion de cartera (HTML)](#6-composicion-de-cartera-html)
7. [Funciones de consulta sobre cache (buscar/top/resolve/fondo)](#7-funciones-de-consulta-sobre-cache-buscartopresolvefondo)
8. [Codigos: tipo_renta, region, horizonte, moneda](#8-codigos-tipo_renta-region-horizonte-moneda)
9. [Cache local](#9-cache-local)
10. [API REST anterior — DISCONTINUADA](#10-api-rest-anterior--discontinuada)
11. [Manejo de errores](#11-manejo-de-errores)
12. [Consideraciones tecnicas](#12-consideraciones-tecnicas)

---

## 1. Resumen de endpoints

| # | Modo CLI | URL | Metodo | Output |
|---|----------|-----|--------|--------|
| 1 | `catalogo` | `https://estadisticas.cafci.org.ar/consulta-de-fondos.json` | GET | JSON ~2.7 MB |
| 2 | `diario` | `https://api.pub.cafci.org.ar/pb_get` | GET | XLSX ~900 KB → JSON normalizado |
| 3 | `ficha FONDO CLASE` | `https://defuddle.md/https://estadisticas.cafci.org.ar/fondos/{F}?clase={C}` | GET | Markdown ~2 KB |
| 4 | `cartera FONDO CLASE` | `https://estadisticas.cafci.org.ar/fondos/{F}?clase={C}` | GET | HTML ~23 KB → JSON parseado |
| 5 | `buscar QUERY` | (sobre catalogo) | local | list de fondos matched |
| 6 | `resolve QUERY` | (sobre catalogo) | local | list {fondo_id, clase_id} |
| 7 | `top CATEGORIA` | (sobre diario) | local | top N por patrimonio |
| 8 | `fondo FONDO CLASE` | (combina 1+2+3+4) | local | ficha completa |
| 9 | `all` | (combina 1+2) | local | snapshot completo |

**Total: 4 endpoints HTTP + 5 funciones de consulta sobre cache.**

---

## 2. Convenciones

### Sin autenticacion

Ninguno de los 4 endpoints requiere API key, token ni cookies. Solo
`/pb_get` historicamente requirio headers de browser para no devolver 403
— al 2026-06 funciona sin ellos pero se siguen enviando por seguridad
contra cambios futuros.

### Headers

**Para `/consulta-de-fondos.json`, `defuddle.md`** y el HTML directo:

```python
HEADERS_BASIC = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}
```

**Para `/pb_get`** (XLSX diario):

```python
HEADERS_BROWSER = {
    **HEADERS_BASIC,
    "Origin": "https://www.cafci.org.ar",
    "Referer": "https://www.cafci.org.ar/",
}
```

### Encoding

Las respuestas estan en **UTF-8 valido**, pero contienen muchos
caracteres acentuados que se muestran como `?` en consolas Windows
(`cp1252`). Workaround: leer con `r.json()`/`r.text` y reescribir con
`json.dumps(..., ensure_ascii=False)` a archivos UTF-8. El script
`fetch_cafci.py` ya hace esto en todos sus outputs.

### Sin parametros de query

Los endpoints HTTP de CAFCI no aceptan filtros server-side. Toda la
filtracion se hace cliente-side sobre los datasets descargados. Por eso
el script cachea ambos datasets por dia y expone funciones (`buscar`,
`top`, `resolve`, `fondo`) que operan sobre el cache.

---

## 3. Catalogo JSON — `/consulta-de-fondos.json`

**URL:** `https://estadisticas.cafci.org.ar/consulta-de-fondos.json`

Catalogo maestro: todos los fondos + clases con IDs, fees, sociedad
gerente/depositaria, tipo de renta, region, moneda, horizonte, ISIN,
Bloomberg ticker, etc. Es la **fuente de verdad para metadata estatica**.

### Tamaño

~2.7 MB. **1152 fondos, 4615 clases** (al 2026-06).

### Schema

```json
{
  "generated_at": "2026-06-04T20:15:37-03:00",
  "total_fondos": 1152,
  "total_clases": 4615,
  "filtros": {
    "tipo_renta":          [{"id": N, "nombre": "..."}, ...],
    "tipo_renta_mixta":    [...],
    "region":              [...],
    "moneda":              [...],
    "benchmark":           [...],
    "duration":            [...],
    "horizonte":           [...],
    "sociedad_gerente":    [...],
    "tipo_dinero":         ["Clasico", "Dinamico", "No Aplica"]
  },
  "fondos": [
    {
      "id": 304,
      "nombre": "1810 Ahorro",
      "codigo_cnv": "394",
      "estado": 1,
      "objetivo": "Administrar una cartera de inversiones de bajo riesgo...",
      "tipo_dinero": "Clasico",
      "valuacion": "D",
      "dias_liquidacion": 0,
      "inicio": "2000-09-14",
      "mm_puro": false,
      "mm_indice": false,
      "sociedad_gerente":   {"id": 241, "nombre": "Proahorro..."},
      "sociedad_depositaria":{"id": 116, "nombre": "Banco Credicoop..."},
      "moneda":             {"id": 1, "nombre": "Peso Argentina"},
      "tipo_renta":         {"id": 4, "nombre": "Mercado de Dinero"},
      "tipo_renta_mixta":   null,
      "region":             {"id": 1, "nombre": "Argentina"},
      "duration":           {"id": 3, "nombre": "Menor o Igual a 1 Año"},
      "benchmark":          {"id": 0, "nombre": "No Registrado"},
      "horizonte":          {"id": 1, "nombre": "Corto Plazo"},
      "clases": [
        {
          "id": 308,
          "nombre": "1810 Ahorro",
          "moneda": {"id": 1, "nombre": "Peso Argentina"},
          "inversion_minima": 5000,
          "honorarios": {
            "ingreso":                 "0.0",
            "rescate":                 "0.0",
            "transferencia":           "0.0",
            "administracion_gerente":  "0.1",
            "administracion_depositaria": "0.15",
            "gasto_ordinario_gestion": "0.0"
          },
          "suscripcion": true,
          "liquidez": true,
          "rg384": false,
          "log_abierto": true,
          "ticker_bloomberg": "1810AHD   ",
          "ticker_isin": null
        }
      ]
    }
  ]
}
```

### Campos de `fondos[]`

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | int | ID interno del fondo. Usar para `ficha`/`cartera`. |
| `nombre` | string | Nombre comercial del fondo. |
| `codigo_cnv` | string | Codigo registral CNV. |
| `estado` | int | `1` = activo (todos los del catalogo). |
| `objetivo` | string | Texto descriptivo del objetivo de inversion. |
| `tipo_dinero` | string | `Clasico`, `Dinamico`, `No Aplica`. |
| `valuacion` | string | `D` (diaria), etc. |
| `dias_liquidacion` | int | Dias habiles para liquidar rescates (0 = inmediata). |
| `inicio` | string | Fecha de inicio ISO `YYYY-MM-DD`. |
| `mm_puro` | bool | Es Money Market puro. |
| `mm_indice` | bool | Indexado a Money Market. |
| `sociedad_gerente`, `sociedad_depositaria` | dict | `{id, nombre}`. |
| `moneda`, `tipo_renta`, `region`, `duration`, `benchmark`, `horizonte` | dict | `{id, nombre}` — categorias. |
| `tipo_renta_mixta` | dict\|null | Solo para Renta Mixta. |
| `clases` | array | Clases del fondo (ver abajo). |

### Campos de `clases[]`

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | int | ID de la clase. Usar para `ficha`/`cartera`. |
| `nombre` | string | Nombre de la clase (ej: "Allaria Equity - Clase A"). |
| `moneda` | dict | `{id, nombre}`. |
| `inversion_minima` | float | Inversion minima en la moneda. |
| `honorarios.ingreso` | string | % comision de suscripcion. |
| `honorarios.rescate` | string | % comision de rescate. |
| `honorarios.transferencia` | string | % comision de transferencia. |
| `honorarios.administracion_gerente` | string | **% anual fee gerente** (clave). |
| `honorarios.administracion_depositaria` | string | **% anual fee depositaria** (clave). |
| `honorarios.gasto_ordinario_gestion` | string | % gastos ordinarios. |
| `suscripcion` | bool | Permite suscripcion. |
| `liquidez` | bool | Permite rescate libre. |
| `rg384` | bool | Apto RG 384/2014 (FCI Cerrados). |
| `log_abierto` | bool | Fondo abierto vs cerrado. |
| `ticker_bloomberg` | string | Ticker en Bloomberg (puede tener padding). |
| `ticker_isin` | string\|null | Codigo ISIN. |

> ⚠️ `honorarios.*` son **strings** (no floats) para preservar precision.
> Castear con `float()` antes de comparar.

---

## 4. Snapshot diario XLSX — `/pb_get`

**URL:** `https://api.pub.cafci.org.ar/pb_get`

Planilla diaria con VCP, patrimonio, market share y variaciones para
todas las clases activas. Es la **fuente para datos de cierre del dia**.

### Tamaño

~900 KB XLSX. Despues de parsear: ~4000 fondos.

### Headers

Historicamente requirio `Origin` + `Referer` para no devolver 403. Al
2026-06 funciona sin ellos pero se siguen enviando.

### Estructura del XLSX

| Fila | Contenido |
|------|-----------|
| 0-6 | Header con titulo, direccion CAFCI |
| 7 | Encabezados nivel 1 (Fondo, Clasificacion, Fecha, Valor, Variacion, etc.) |
| 8 | Encabezados nivel 2 (Moneda, Region, Horizonte, Actual, dia anterior, etc.) |
| 9 | Vacia |
| 10 | **Nombre de categoria** (solo col 0 populada) |
| 11+ | Fondos de esa categoria (hasta proxima categoria) |

Las **categorias** combinan `tipo_renta + moneda + region` como string:
- `Renta Variable Peso Argentina`
- `Mercado de Dinero Peso Argentina`
- `Renta Fija Dolar Estadounidense Argentina`
- etc.

### Columnas usadas (de 47 totales, solo 19 utiles)

| Idx | Nombre | Descripcion |
|-----|--------|-------------|
| 0 | Fondo | Nombre completo de la clase. |
| 1 | Moneda | `ARS`, `USD`, `USB`. |
| 2 | Region | `Arg`, `Lat`, `Glo`. |
| 3 | Horizonte | `Cor`, `Med`, `Largo`, `Flex`. |
| 4 | Fecha | Fecha del VCP (DD/MM/YY). |
| 5 | VCP Actual | Valor cuotaparte de hoy. |
| 6 | VCP Anterior | Valor cuotaparte del dia habil anterior. |
| 7 | Variac. % | % vs dia anterior. |
| 8 | Reexp. Pesos | VCP reexpresado en pesos (= col 5 para ARS). |
| 9 | Variac. mes | % vs ultimo dia mes anterior. |
| 10 | Variac. YTD | % vs cierre año anterior. |
| 11 | Variac. 12m | % vs hace 12 meses. |
| 12 | Cuotapartes | Cantidad de cuotapartes en circulacion. |
| 14 | Patrimonio | **Patrimonio neto** en moneda del fondo. |
| 16 | Market Share | % del patrimonio total. |
| 17 | Depositaria | Sociedad depositaria. |
| 18 | Codigo CNV | Codigo CNV. |

### Schema del response normalizado (despues de `_parse_xlsx`)

```json
{
  "fecha_reporte": "2026-06-04",
  "categorias": ["Renta Variable Peso Argentina", "..."],
  "fondos": [
    {
      "nombre": "Allaria Equity Selection - Clase A",
      "categoria": "Renta Variable Peso Argentina",
      "moneda": "ARS",
      "region": "Arg",
      "horizonte": "Cor",
      "fecha": "2026-06-04",
      "vcp_actual": 1642.85,
      "vcp_anterior": 1628.345,
      "variacion_dia_pct": 0.891,
      "vcp_reexp_pesos": 1642.85,
      "variacion_mes_pct": -1.181,
      "variacion_ytd_pct": 11.939,
      "variacion_12m_pct": 61.542,
      "cantidad_cuotapartes": 1276470413.29,
      "patrimonio": 2097049572.01,
      "market_share": 0.107,
      "depositaria": "Banco Comafi S.A.",
      "codigo_cnv": "1603"
    }
  ]
}
```

### Join con catalogo

Para joinear catalogo + diario usar:
- `CATALOGO.clases[].nombre` (exacto)  ↔  `DIARIO.fondos[].nombre`

NO usar `id` — el diario no expone IDs.

---

## 5. Ficha individual (Markdown) — defuddle.md

**URL:** `https://defuddle.md/https://estadisticas.cafci.org.ar/fondos/{fondoId}?clase={claseId}`

Defuddle es un proxy que convierte HTML a Markdown limpio. Ideal para
mostrarle el contenido al usuario o al agente sin ruido de HTML.

### Tamaño

~2 KB de markdown.

### Contenido extraido

| Seccion | Detalle |
|---------|---------|
| **Rendimiento Historico (TNA)** | Tabla con VCP + 7 dias, 1 mes, 90 dias, 180 dias, En el año (YTD), 12 meses. Todos en **TNA % sobre dias corridos**. |
| **Valores al [fecha]** | Patrimonio bajo administracion, valor cuotaparte, valor por mil. |
| **Composicion de Cartera** | Solo fecha (la composicion real esta en el HTML — ver seccion 6). |
| **Honorarios y Comisiones** | Gerente, depositaria, ingreso, egreso, transferencia, gastos ordinarios, comision de exito. |
| **Datos del Fondo** | Administradora, depositaria, tipo de renta, tipo de DD, region, benchmark, horizonte, duration, moneda, codigo CNV. |
| **Inversion minima** | Monto + moneda. |
| **Plazo de Liquidacion** | Dias habiles. |

### Ejemplo de seccion principal

```markdown
### Rendimiento Historico (TNA) — al 04/06/2026

| Periodo | 1810 Ahorro |
| --- | --- |
| Valor Cuotaparte | 226.415,581 |
| 7 dias | 17,9481 % |
| 1 mes | 18,1627 % |
| 90 dias | 20,2972 % |
| 180 dias | 22,953 % |
| En el año | 23,3481 % |
| 12 meses | 30,1081 % |
```

> **TNA** = Tasa Nominal Anual sobre dias corridos.

---

## 6. Composicion de cartera (HTML)

**URL:** `https://estadisticas.cafci.org.ar/fondos/{fondoId}?clase={claseId}`

El HTML directo de la pagina del fondo contiene la composicion completa
de cartera embebida como **atributo HTML del elemento `<canvas>`**:

```html
<canvas data-pie-chart-items-value="[{&quot;nombre&quot;:&quot;Cta Cte $...&quot;,...}]">
```

Defuddle no captura ese atributo. Hay que parsear el HTML directo y
extraer con regex.

### Tamaño

~23 KB de HTML.

### Parser

```python
import re, html, json

m_date = re.search(r'class="valores">Valores al ([^<]+)<', h)
m_pie  = re.search(r'data-pie-chart-items-value="([^"]+)"', h)
composicion = json.loads(html.unescape(m_pie.group(1)))
```

### Schema

```json
{
  "fecha_cartera": "15/05/2026",
  "composicion": [
    {"nombre": "Cta Cte $ Rem Bco Credico", "porcentaje": 17.4},
    {"nombre": "Pzo Fi $ Bco Nacion", "porcentaje": 14.8},
    {"nombre": "Pzo Fi $ Bco Santander Ri", "porcentaje": 13.3},
    {"nombre": "Caucion Colocadora $ BYMA", "porcentaje": 10.3},
    ...
    {"nombre": "Resto de Activos", "porcentaje": 29.2}
  ]
}
```

### Limitaciones

- CAFCI publica solo los **top ~14 activos** + `"Resto de Activos"` agrupado.
- No hay desglose completo posicion-por-posicion.
- La fecha de cartera es ~2-3 semanas atrasada vs `fecha_reporte` del diario
  (las composiciones se publican con delay).

---

## 7. Funciones de consulta sobre cache (buscar/top/resolve/fondo)

Estas no son endpoints HTTP — son funciones del script `fetch_cafci.py`
que operan sobre los datasets cacheados (catalogo + diario).

### `buscar QUERY`

Busca fondos por nombre parcial (case-insensitive) en el catalogo.
Devuelve lista con id, nombre, tipo_renta, sociedad_gerente y resumen de
clases con honorarios.

### `resolve QUERY`

Mas compacto: devuelve solo `{fondo_id, fondo_nombre, clase_id, clase_nombre}`.
Util para pipelining (resolve → fondo).

### `top CATEGORIA --limit N`

Top N fondos por patrimonio en una categoria del diario. La categoria
debe matchear exacto el string del diario (ej: `"Mercado de Dinero Peso Argentina"`).

### `fondo FONDO_ID CLASE_ID` (all-in-one)

Combina los 4 endpoints en un solo dict:
- `meta`: del catalogo (nombre, fees, sociedad gerente, tipo_renta, ...)
- `diario`: del XLSX (patrimonio actual, variaciones)
- `ficha_md`: markdown de defuddle (rendimientos por periodo)
- `cartera`: composicion top activos

---

## 8. Codigos: tipo_renta, region, horizonte, moneda

### `tipo_renta` (10 categorias)

| id | nombre |
|----|--------|
| 2 | Renta Variable |
| 3 | Renta Fija |
| 4 | Mercado de Dinero |
| 5 | Renta Mixta |
| 6 | PyMes |
| 7 | Retorno Total |
| 8 | Infraestructura |
| 9 | Fondos Cerrados |
| 10 | ASG (Ambiental, Social y de Gobernanza) |
| 11 | RG900 |

### `region` (6 categorias)

| id | nombre |
|----|--------|
| 0 | <Sin Asignar> |
| 1 | Argentina |
| 2 | Latinoamerica |
| 3 | Europa |
| 5 | Brasil |
| 7 | Global |

### `horizonte` (5 categorias)

| id | nombre |
|----|--------|
| 0 | <Sin Asignar> |
| 1 | Corto Plazo |
| 2 | Mediano Plazo |
| 3 | Largo Plazo |
| 4 | Plazo Flexible |

### `moneda` (3 categorias en CATALOGO)

| id | nombre | abreviado en DIARIO |
|----|--------|---------------------|
| 1 | Peso Argentina | `ARS` |
| 2 | Dolar Estadounidense | `USD` |
| 180 | Dolar Estadounidense Billete | `USB` |

### `tipo_dinero`

`Clasico`, `Dinamico`, `No Aplica`. Solo aplica para fondos de Mercado de Dinero.

### `duration` (6 categorias)

| id | nombre |
|----|--------|
| 1 | Mayor a 0.5 y Menor Igual 1 Año |
| 2 | Menor o Igual a 0.5 Año |
| 3 | Menor o Igual a 1 Año |
| 4 | Mayor a 1 y Menor Igual 3 Años |
| 5 | Mayor a 3 Años |

### `benchmark` (13 categorias)

Ej: `30%+70%`, `A3500`, `Badlar`, `CER + 2%`, `Inflacion+3%`, etc.

### Region en DIARIO (abreviado)

| Abreviado | Significado |
|-----------|-------------|
| `Arg` | Argentina |
| `Lat` | Latinoamerica |
| `Glo` | Global |

### Horizonte en DIARIO (abreviado)

| Abreviado | Significado |
|-----------|-------------|
| `Cor` | Corto Plazo |
| `Med` | Mediano Plazo |
| `Largo` | Largo Plazo |
| `Flex` | Plazo Flexible |

---

## 9. Cache local

Para evitar pegar a la API en cada consulta, el script cachea los
datasets pesados por dia en el directorio temporal del sistema:

```
$TMP/cafci-catalog-YYYY-MM-DD.json   (~2.7 MB, regenerable)
$TMP/cafci-daily-YYYY-MM-DD.json     (~1-2 MB, regenerable)
$TMP/cafci-daily-YYYY-MM-DD.xlsx     (~900 KB, intermedio)
```

- En Windows: `C:\Users\<user>\AppData\Local\Temp\`.
- En Linux/Mac: `/tmp/`.

Cada llamada chequea si el cache del dia existe. Si si: lo lee. Si no:
descarga y guarda.

**Forzar refetch:** pasar `--no-cache` al script.

**Por que cachear:** el catalogo y el diario son archivos grandes
relativamente lentos de descargar y parsear, pero solo cambian una vez
por dia. Si vas a hacer 10 consultas en un dia, querer 10 descargas no
tiene sentido.

---

## 10. API REST anterior — DISCONTINUADA

Hasta 2026-04 CAFCI exponia una API REST con los siguientes paths:

```
https://api.pub.cafci.org.ar/tipo-renta
https://api.pub.cafci.org.ar/fondo/{id}
https://api.pub.cafci.org.ar/estadisticas/informacion/diaria/{YYYY-MM-DD}
```

**Estado actual:** todas retornan **HTTP 403** con body:

```json
{"error":"Route not allowed"}
```

Verificado al 2026-06-05. **No usar ni intentar reactivar** — el 403 es
deliberado en CloudFront edge.

El unico path que sigue activo en `api.pub.cafci.org.ar` es `/pb_get`
(devuelve el XLSX). Cualquier otro path retorna 403.

---

## 11. Manejo de errores

| Status | Causas tipicas |
|--------|----------------|
| 200 | OK — verificar tamaño del body para no procesar contenido vacio. |
| 403 `Route not allowed` | Path discontinuado de la API REST anterior. |
| 403 (sin body claro) | Faltan headers de browser en `/pb_get`. Agregar `Origin` + `Referer`. |
| 404 | URL mal formada en `defuddle.md` o IDs inexistentes. |
| Connection timeout en `defuddle.md` | El proxy puede colgarse. Reintentar 1 vez con backoff. |

### Errores comunes en el dataset

- `total_fondos == 0` en CATALOGO: posible caida temporal del backend. Reintentar.
- `fondos[]` vacio en DIARIO: revisar que es dia habil (fin de semana = sin update).
- Fondo en CATALOGO sin match en DIARIO: revisar `clases[].nombre` exacto vs `fondos[].nombre`. Algunos fondos del catalogo no operan ese dia.
- `composicion: []` en cartera: la pagina HTML no expuso el atributo `data-pie-chart-items-value` (algunos fondos cerrados no lo publican).

---

## 12. Consideraciones tecnicas

### Rate limiting

No hay rate limiting documentado. Recomendado:
- Minimo **0.3 segundos** entre requests a CAFCI.
- Defuddle.md (proxy externo) puede ser mas lento — esperar mas si se notan timeouts.
- Para batches grandes (ej: 100 fichas), usar pool de concurrencia max 5.

### Delay de los datos

- **Catalogo**: actualizado con cada cambio (`generated_at` en el response). Suele actualizarse 1x al dia.
- **Diario**: planilla del dia se publica al cierre de operatoria (~18hs ART). Fines de semana y feriados: ultimo dia habil.
- **Composicion de cartera**: ~2-3 semanas atrasada vs `fecha_reporte` del diario (delay regulatorio).

### CORS

Los endpoints aceptan requests de cualquier origen. Para uso desde
frontend, considerar proxy de cache.

### Encoding

Todas las respuestas son UTF-8 valido. Tener en cuenta que:
- Windows consola (cp1252) muestra `?` para acentos — usar archivo UTF-8.
- El XLSX usa fechas como `date` objects de openpyxl — castear con `to_iso_date()`.
- `ticker_bloomberg` puede tener padding de espacios — `strip()` antes de usar.

### Cache cuotidiano

El script cachea catalogo + diario por dia. Si la API publica un update
intra-dia (raro), forzar `--no-cache` para refetch.

### Aviso legal

- Fuentes publicas del CAFCI sin documentacion oficial.
- Los endpoints pueden cambiar sin aviso (como ya paso con la API REST en 2026-04).
- Para uso comercial intensivo, contactar al CAFCI para feeds oficiales.
- Rendimientos pasados no garantizan rendimientos futuros.

---

## Referencias

- **CAFCI Oficial:** https://www.cafci.org.ar
- **Estadisticas:** https://estadisticas.cafci.org.ar
- **CNV (regulador):** https://www.cnv.gov.ar
- **defuddle.md** (proxy HTML→MD): https://defuddle.md
- **Skill original (referencia conceptual):** [ferminrp/agent-skills/cafci-fondos-comunes-argentina](https://github.com/ferminrp/agent-skills/tree/main/skills/cafci-fondos-comunes-argentina) — esta implementacion sigue su mismo diseño de 4 fuentes pero portado a la arquitectura SKILL.md/REFERENCE.md/fetch_*.py del repo `gauss314/skills`.
