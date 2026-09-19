# INDEC Argentina — Referencia Completa

> **API de Series de Tiempo de la Republica Argentina** — la API oficial del
> Estado Argentino que agrega series de datos de **multiples organismos
> publicos**: INDEC, BCRA, Ministerio de Economia, Secretaria de Trabajo,
> entre otros. **Sin auth, sin API key, JSON estructurado y documentacion
> oficial publica.**

---

## Indice

1. [Que es esta API](#1-que-es-esta-api)
2. [Por que usarla](#2-por-que-usarla)
3. [Hosts y endpoints](#3-hosts-y-endpoints)
4. [Convenciones generales](#4-convenciones-generales)
5. [Quick reference de parametros](#5-quick-reference-de-parametros)
6. [Quick reference de modos del CLI](#6-quick-reference-de-modos-del-cli)
7. [Organismos publicadores cubiertos](#7-organismos-publicadores-cubiertos)
8. [Documentos relacionados](#8-documentos-relacionados)

---

## 1. Que es esta API

La **API de Series de Tiempo de la Republica Argentina** (`apis.datos.gob.ar/series`)
es el endpoint oficial del Estado para acceder a series historicas de
indicadores publicos argentinos.

**No es una API "del INDEC" exclusivamente** — es un **agregador del Estado**
que centraliza datos publicados por varios organismos. La fuente real de cada
serie esta indicada en el campo `dataset.source` del response.

### Caracteristicas clave

- **~4,250 series totales** indexadas al 2026-06.
- **JSON o CSV** en el response (selectable via param `format`).
- **Sin API key, sin auth, sin token, sin captcha.** Acceso publico al 100%.
- Mantenida por la **Direccion Nacional de Datos e Informacion Publica**
  (`datos.gob.ar`).
- API estable desde 2017+ con politicas de **no-break ABI**.
- **Documentacion oficial completa**: [datosgobar.github.io/series-tiempo-ar-api](https://datosgobar.github.io/series-tiempo-ar-api/)
- Codigo abierto en GitHub: [datosgobar/series-tiempo-ar-api](https://github.com/datosgobar/series-tiempo-ar-api)

### Que tipo de datos contiene

| Categoria | Ejemplos |
|-----------|----------|
| **Precios** | IPC Nacional, IPC GBA, IPP, IPC categoria, IPC CABA |
| **Actividad economica** | EMAE, IPI, ISAC, PIB, capacidad instalada |
| **Empleo** | EPH, desempleo, salarios RIPTE, SMVM |
| **Pobreza** | Linea de pobreza, indigencia, canasta basica |
| **Comercio exterior** | Exportaciones, importaciones, balanza comercial |
| **Monetario/financiero** | Tipo de cambio, tasas, reservas BCRA, REM expectativas |
| **Demografia** | Poblacion, censos |
| **Sector publico** | Recursos tributarios, deuda publica |

---

## 2. Por que usarla

### Ventajas vs scraping del sitio INDEC

| Feature | Esta API | Scraping indec.gob.ar |
|---------|:--------:|:---------------------:|
| Datos estructurados JSON | ✅ | ❌ (PDF / Excel) |
| Acceso programatico | ✅ | ⚠️ frágil |
| Sin auth | ✅ | ✅ |
| Cobertura | ~4,250 series | Limitada a publicaciones |
| Filtros server-side (start_date, end_date, etc.) | ✅ | ❌ |
| Transformaciones builtin (% YoY, agregaciones) | ✅ | ❌ (calcular cliente-side) |
| Documentacion oficial | ✅ | ❌ |

### Ventajas vs API REST manuales

A diferencia de scrapers de Google Finance, TradingView, etc., esta API:

- **Es oficial y publica del Estado** — pensada para uso por terceros.
- **Estable**: mantenida con politicas de versionado y no-break.
- Tiene **documentacion oficial completa**.
- Tiene **codigo abierto en GitHub** — podes ver issues, contribuir, ver
  changelogs.

### Diferenciales unicos vs otros skills del repo

| Feature | INDEC | bcra-macro | FRED Macro |
|---------|:--:|:--:|:--:|
| Sin auth | ✅ | ✅ | ❌ (requiere API key) |
| Cobertura INDEC oficial completa | ✅ | ⚠️ overlap parcial | ❌ |
| Cobertura BCRA | ⚠️ subset | ✅ 638 series | ❌ |
| Multi-organismo | ✅ INDEC + BCRA + Min.Econ. + STyE | ❌ solo BCRA | ✅ global |
| Transformaciones builtin (% YoY, YTD, change) | ✅ | ❌ | ⚠️ requiere FRED transform |
| Agregacion temporal builtin (daily→monthly) | ✅ | ❌ | ⚠️ |
| Multi-serie en una request | ✅ | ❌ | ❌ |
| Documentacion oficial | ✅ | ✅ | ✅ |

**Cuando usar este skill vs `bcra-macro`:**
- Para series del **INDEC** (IPC, EMAE, EPH, PIB) → este skill.
- Para series del **BCRA exclusivamente** (BADLAR, CER, UVA, M2, etc.) → `bcra-macro` tiene mas cobertura.
- Para **datos cruzados entre INDEC + BCRA** → este skill (todo en un endpoint).

---

## 3. Hosts y endpoints

### Host

```
https://apis.datos.gob.ar/series/api/
```

### Endpoints

| Endpoint | Funcion | Documento detallado |
|----------|---------|---------------------|
| `/series` | Fetch de datos por IDs (endpoint principal) | [ENDPOINTS.md](./ENDPOINTS.md) |
| `/search` | Buscador full-text de series | [ENDPOINTS.md](./ENDPOINTS.md) |
| `/dump` | Descarga completa del catalogo | [ENDPOINTS.md](./ENDPOINTS.md) |
| `/validate` | Valida una query antes de ejecutarla | [ENDPOINTS.md](./ENDPOINTS.md) |

---

## 4. Convenciones generales

### Headers minimos

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}
```

No requiere `X-Same-Domain`, `Origin`, `Referer` ni cookies. La API es
acreditadamente publica.

### Formato de IDs de series

Los IDs son criptos pero consistentes:

```
{dataset_id}.{distribution_id}_{slug}_{base}_{freq}_{field_index}

Ejemplo: 145.3_INGNACUAL_DICI_M_38
        ↑   ↑  ↑          ↑    ↑ ↑
        |   |  |          |    | └─ field index dentro de la distribucion
        |   |  |          |    └─── frequency code (M=monthly, T=trimestral, A=annual, D=daily)
        |   |  |          └──────── base (DICI = base diciembre)
        |   |  └────────────────── slug del indicador (INGNACUAL = IPC nacional)
        |   └──────────────────── distribution ID
        └──────────────────────── dataset ID
```

> **No intentar adivinar IDs.** Usar `/search` para descubrirlos, o el catalogo
> curado en [`../assets/known_series_ids.json`](../assets/known_series_ids.json).

### Encoding

UTF-8 valido en TODOS los responses. Sin issues de encoding como en MAE o
Google Finance.

### Rate limiting

No documentado, no observado. La API tolera al menos 5 req/seg sin throttle.
Recomendado mantener < 5 req/seg por buena ciudadania.

### Limites de respuesta

- **Maximo 1,000 datapoints por serie por request**. Para series mas largas:
  paginar con `start` (offset).
- Sin limit por defecto: el server impone el max 1,000 automaticamente.

---

## 5. Quick reference de parametros

Ver detalles completos en [PARAMS.md](./PARAMS.md).

### Params del endpoint `/series`

| Param | Valores | Default | Descripcion |
|-------|---------|---------|-------------|
| `ids` | string CSV | (requerido) | IDs separados por coma. Hasta varios en una llamada. |
| `format` | `json` / `csv` | `json` | Formato del response. |
| `start_date` | YYYY-MM-DD | — | Filtro temporal desde. |
| `end_date` | YYYY-MM-DD | — | Filtro temporal hasta. |
| `representation_mode` | ver tabla abajo | `value` | Transformacion de los valores. |
| `collapse` | `day` / `week` / `month` / `quarter` / `semester` / `year` | — | Agregacion temporal. |
| `collapse_aggregation` | `avg` / `sum` / `end_of_period` / `min` / `max` | `avg` | Modo de agregacion. |
| `limit` | int (max 1000) | 100 | Datapoints por serie. |
| `start` | int | 0 | Offset para paginacion. |
| `last` | int | — | Devuelve los ultimos N valores. ⚠️ INCOMPATIBLE con sort/start/limit. |
| `sort` | `asc` / `desc` | `asc` | Orden. |
| `metadata` | `none` / `only` / `simple` / `full` | `full` | Nivel de metadata. |
| `header` | `titles` / `ids` / `descriptions` | `titles` | Header del CSV (solo format=csv). |

### Representation modes (transformaciones builtin)

Ver [REPRESENTATION_MODES.md](./REPRESENTATION_MODES.md) con ejemplos.

| Modo | Descripcion |
|------|-------------|
| `value` | Valor original (default) |
| `change` | Diff absoluta vs periodo anterior |
| `percent_change` | Var % vs periodo anterior (inflacion mensual para IPC) |
| `change_a_year_ago` | Diff absoluta YoY |
| `percent_change_a_year_ago` | Var % YoY (**inflacion interanual** para IPC) |
| `change_since_beginning_of_year` | Diff absoluta YTD |
| `percent_change_since_beginning_of_year` | Var % YTD (**inflacion acumulada año** para IPC) |

### Collapse temporal

Ver [COLLAPSE_AGGREGATIONS.md](./COLLAPSE_AGGREGATIONS.md) con ejemplos.

| Collapse | Convierte a |
|----------|-------------|
| `day` | Diario |
| `week` | Semanal |
| `month` | Mensual |
| `quarter` | Trimestral |
| `semester` | Semestral |
| `year` | Anual |

Combinado con `collapse_aggregation`: `avg` / `sum` / `end_of_period` / `min` / `max`.

---

## 6. Quick reference de modos del CLI

Ver ejemplos completos en [COOKBOOK.md](./COOKBOOK.md).

### Consulta directa (4 modos)

| Modo | Descripcion |
|------|-------------|
| `series IDS` | Fetch por ID(s) — el modo mas potente |
| `search QUERY` | Busca series por keywords |
| `validate IDS` | Valida que un ID sea correcto |
| `dump` | Catalogo completo (pesado) |

### Atajos por indicador (9 modos)

| Modo | Que devuelve | RPC INDEC IDs |
|------|--------------|---------------|
| `ipc` | IPC Nacional var mensual | `145.3_INGNACUAL_DICI_M_38` |
| `ipc-completo` | IPC + nucleo + regulados + categorias | 5 IDs combinadas |
| `emae` | EMAE original + desestacionalizado | 2 IDs |
| `salarios` | RIPTE + SMVM + haber jubilatorio | 5 IDs |
| `comercio` | Exportaciones totales (M/T/A) | 3 IDs |
| `construccion` | ISAC nivel general | 2 IDs |
| `dolar` | Tipo de cambio BNA diario | 1 ID (BCRA) |
| `reservas` | Reservas internacionales BCRA | 4 IDs (BCRA) |
| `snapshot` | Macro snapshot | 5 IDs combinadas |

### Catalogos locales (5 modos)

| Modo | Que devuelve |
|------|--------------|
| `catalog` | Catalogo curado de series IDs |
| `groups` | Bundles pre-armados |
| `sources` | Organismos publicadores |
| `modes` | Representation modes |
| `aggregations` | Collapse aggregations |

### Combinado (1 modo)

| Modo | Que devuelve |
|------|--------------|
| `all` | Snapshot macro completo: IPC + EMAE + salarios + dolar + reservas + construccion + comercio |

---

## 7. Organismos publicadores cubiertos

Ver detalle en [DATA_SOURCES.md](./DATA_SOURCES.md).

| Source | Cobertura tipica |
|--------|-----------------|
| **INDEC** | IPC, EMAE, IPI, ISAC, EPH, pobreza, censos, comercio exterior |
| **BCRA** | Reservas, tasas, tipo cambio, REM expectativas, balance cambiario |
| **Ministerio de Economia** | PIB, deuda publica, recursos tributarios |
| **Secretaria de Trabajo, Empleo y Seguridad Social** | RIPTE, SMVM, haber jubilatorio |
| **Subsecretaria de Programacion Macroeconomica** | IPC GBA historico, PIB en USD |
| **DGEYC (CABA)** | IPC Ciudad de Buenos Aires |

---

## 8. Documentos relacionados

| Documento | Que contiene |
|-----------|-------------|
| [ENDPOINTS.md](./ENDPOINTS.md) | Cada uno de los 4 endpoints en profundidad |
| [PARAMS.md](./PARAMS.md) | Todos los parametros del /series con ejemplos |
| [REPRESENTATION_MODES.md](./REPRESENTATION_MODES.md) | Las 6 modes con ejemplos calculados |
| [COLLAPSE_AGGREGATIONS.md](./COLLAPSE_AGGREGATIONS.md) | Agregacion temporal con casos |
| [SERIES_CATALOG.md](./SERIES_CATALOG.md) | IDs canonicos organizados por topico (con descripciones) |
| [RESPONSE_FORMAT.md](./RESPONSE_FORMAT.md) | Schema JSON / CSV con todos los campos |
| [DATA_SOURCES.md](./DATA_SOURCES.md) | Detalle de cada publicador y sus datasets |
| [COOKBOOK.md](./COOKBOOK.md) | **30+ recetas listas para copy-paste** |
| [LIMITATIONS_TROUBLESHOOTING.md](./LIMITATIONS_TROUBLESHOOTING.md) | Limites, errores comunes, debugging |
| [`../assets/known_series_ids.json`](../assets/known_series_ids.json) | Catalogo curado de series IDs |
| [`../assets/series_groups.json`](../assets/series_groups.json) | Bundles pre-armados |
| [`../assets/representation_modes.json`](../assets/representation_modes.json) | Modes con ejemplos |
| [`../assets/collapse_aggregations.json`](../assets/collapse_aggregations.json) | Aggregations con ejemplos |
| [`../assets/data_sources.json`](../assets/data_sources.json) | Publicadores estructurados |

---

## Referencias externas

- **Documentacion oficial:** https://datosgobar.github.io/series-tiempo-ar-api/
- **GitHub:** https://github.com/datosgobar/series-tiempo-ar-api
- **Portal datos.gob.ar:** https://datos.gob.ar
- **INDEC oficial:** https://www.indec.gob.ar
- **BCRA oficial:** https://www.bcra.gob.ar
