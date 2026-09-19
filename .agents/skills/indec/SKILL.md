---
name: indec
description: "Datos macro y sociales de Argentina via la API oficial Series de Tiempo del Estado (apis.datos.gob.ar/series). ~4250 series del INDEC + BCRA + Min Economia + Sec Trabajo. Sin auth, sin API key. IPC nacional, EMAE, IPI, ISAC, EPH (desempleo), pobreza, comercio exterior, salarios (RIPTE, SMVM), tipo de cambio, reservas, REM expectativas. Transformaciones builtin (% YoY, % YTD, change) y agregacion temporal (daily→monthly→yearly) server-side. La API mas estable y mejor documentada del repo."
license: MIT
---

# INDEC Argentina — API Oficial de Series de Tiempo

Skill **premium** para extraer datos macroeconomicos y sociales de
Argentina via la **API oficial del Estado Argentino**:
`apis.datos.gob.ar/series` — sin API key, sin autenticacion, con
documentacion oficial y politicas de no-break ABI.

A diferencia de skills basados en APIs internas (TradingView, Google
Finance), **esta es una API PUBLICA OFICIAL** mantenida por la Direccion
Nacional de Datos e Informacion Publica. Es **la API mas estable y
confiable de todo el repositorio.**

---

## 🎯 Que datos cubre

**~4,250 series totales** del catalogo oficial, agregando datos de
multiples organismos publicos argentinos:

| Organismo | Tipo de datos |
|-----------|---------------|
| **INDEC** | IPC nacional, IPC GBA, EMAE, IPI, ISAC, EPH (empleo/desempleo), pobreza, censos, comercio exterior, PIB |
| **BCRA** | Tipo de cambio, reservas, REM expectativas, balance cambiario, tasas |
| **Min Economia** | PIB cuentas nacionales, deuda publica, fiscal |
| **Sec Trabajo (MTEySS)** | RIPTE, SMVM, haber jubilatorio |
| **DGEYC (CABA)** | IPC Ciudad de Buenos Aires |

---

## 🚀 Quick start

```bash
# Snapshot rapido de la economia argentina
py scripts/fetch_indec.py snapshot --last 3

# IPC ultimos 12 meses
py scripts/fetch_indec.py ipc --last 12

# EMAE original + desestacionalizado
py scripts/fetch_indec.py emae --last 12

# Tipo de cambio diario → cierre mensual
py scripts/fetch_indec.py dolar --collapse month --aggregation end_of_period --last 12

# Buscar serie por keyword
py scripts/fetch_indec.py search "pobreza" --limit 10

# Serie por ID con transformacion (var YoY)
py scripts/fetch_indec.py series "145.3_INGNACUAL_DICI_M_38" --mode percent_change_a_year_ago --last 12
```

---

## ⚡ Lo unico que hace este skill

Tres killer features de esta API (no disponibles en otros skills del repo):

### 1. Transformaciones builtin server-side

Pedir **inflacion interanual** o **acumulada YTD** directamente desde el
indice IPC, sin calcular cliente-side:

```bash
# Inflacion interanual ya calculada
py scripts/fetch_indec.py series "<ID_IPC_INDICE>" --mode percent_change_a_year_ago
```

Modos disponibles: `value`, `change`, `percent_change`,
`percent_change_a_year_ago` (**inflacion YoY**),
`percent_change_since_beginning_of_year` (**inflacion YTD**),
`change_a_year_ago`, `change_since_beginning_of_year`.

Ver [`references/REPRESENTATION_MODES.md`](./references/REPRESENTATION_MODES.md).

### 2. Agregacion temporal builtin

Convertir serie diaria a mensual/anual directamente en el server:

```bash
# Dolar diario → cierre mensual
py scripts/fetch_indec.py dolar --collapse month --aggregation end_of_period
```

Collapses: `day`, `week`, `month`, `quarter`, `semester`, `year`.
Aggregations: `avg`, `sum`, `end_of_period`, `min`, `max`.

Ver [`references/COLLAPSE_AGGREGATIONS.md`](./references/COLLAPSE_AGGREGATIONS.md).

### 3. Multi-serie en una sola request

Combinar IPC + RIPTE + dolar en 1 request:

```bash
py scripts/fetch_indec.py series "145.3_INGNACUAL_DICI_M_38,158.1_REPTE_0_0_5,168.1_T_CAMBIOR_D_0_0_26" --last 12
```

---

## Estructura del skill

```
skills/indec/
├── SKILL.md                                # Este archivo
├── references/                             # 10 documentos exhaustivos
│   ├── REFERENCE.md                        # Overview general
│   ├── ENDPOINTS.md                        # Deep dive de los 4 endpoints
│   ├── PARAMS.md                           # Cada parametro explicado
│   ├── REPRESENTATION_MODES.md             # Las 7 transformaciones
│   ├── COLLAPSE_AGGREGATIONS.md            # Agregacion temporal
│   ├── SERIES_CATALOG.md                   # IDs canonicos por topico
│   ├── RESPONSE_FORMAT.md                  # Schema JSON / CSV completo
│   ├── DATA_SOURCES.md                     # Organismos publicadores
│   ├── COOKBOOK.md                         # 30+ recetas
│   └── LIMITATIONS_TROUBLESHOOTING.md      # Limites + errores comunes
├── assets/                                 # 5 archivos JSON
│   ├── known_series_ids.json               # Catalogo curado de IDs
│   ├── series_groups.json                  # Bundles pre-armados
│   ├── representation_modes.json           # Modes con ejemplos
│   ├── collapse_aggregations.json          # Aggregations con ejemplos
│   └── data_sources.json                   # Publicadores estructurados
└── scripts/
    └── fetch_indec.py                      # Script con 19 modos CLI
```

---

## 19 modos CLI disponibles

### Consulta directa (4 modos)

| Modo | Descripcion |
|------|-------------|
| `series IDS` | Fetch por ID(s) — el modo mas potente |
| `search QUERY` | Busca series por keywords |
| `validate IDS` | Valida que un ID sea correcto |
| `dump` | Catalogo completo (pesado, ~MBs) |

### Atajos por indicador (9 modos)

| Modo | Que devuelve | IDs combinados |
|------|--------------|----------------|
| `ipc` | IPC Nacional var mensual | 1 ID |
| `ipc-completo` | IPC + nucleo + regulados + categorias | 5 IDs |
| `emae` | EMAE original + desestacionalizado | 2 IDs |
| `salarios` | RIPTE + SMVM + haber jubilatorio | 5 IDs |
| `comercio` | Exportaciones totales (M/T/A) | 3 IDs |
| `construccion` | ISAC nivel general | 2 IDs |
| `dolar` | Tipo de cambio BNA diario | 1 ID (BCRA) |
| `reservas` | Reservas internacionales BCRA | 4 IDs (BCRA) |
| `snapshot` | Snapshot macro Argentina | 5 IDs combinadas |

### Catalogos locales (5 modos)

| Modo | Que devuelve |
|------|--------------|
| `catalog` | Catalogo curado de series IDs principales |
| `groups` | Bundles pre-armados |
| `sources` | Organismos publicadores |
| `modes` | Representation modes disponibles |
| `aggregations` | Collapse aggregations disponibles |

### Combinado (1 modo)

| Modo | Que devuelve |
|------|--------------|
| `all` | Snapshot macro completo: IPC + EMAE + salarios + dolar + reservas + construccion + comercio |

---

## Flags principales

| Flag | Descripcion |
|------|-------------|
| `--start YYYY-MM-DD` | Fecha desde |
| `--end YYYY-MM-DD` | Fecha hasta |
| `--last N` | Ultimos N valores (⚠️ incompatible con sort/start/limit) |
| `--mode X` | Representation mode (value / percent_change / percent_change_a_year_ago / etc.) |
| `--collapse X` | Agregacion temporal (day/week/month/quarter/semester/year) |
| `--aggregation X` | Modo de agregacion (avg/sum/end_of_period/min/max) |
| `--limit N` | Datapoints por serie (max 1000) |
| `--offset N` | Offset para paginacion |
| `--sort asc/desc` | Orden |
| `--metadata X` | Verbosidad (none/only/simple/full) |
| `--format X` | json o csv |
| `--raw` | Response sin normalizar |
| `-o file` | Guardar a archivo |
| `-q` | Silencioso |

---

## Diferencial vs `bcra-macro` y otros skills

| Feature | `indec` | `bcra-macro` | FRED |
|---------|:--:|:--:|:--:|
| Sin auth | ✅ | ✅ | ❌ requiere key |
| Cobertura INDEC completa | ✅ | ❌ | ❌ |
| Cobertura BCRA | ⚠️ subset | ✅ 638 series | ❌ |
| Multi-organismo | ✅ INDEC + BCRA + Min Econ | ❌ solo BCRA | ✅ global |
| Transformaciones builtin (% YoY, YTD) | ✅ **UNICO** | ❌ | ⚠️ requiere FRED transform |
| Agregacion temporal builtin | ✅ **UNICO** | ❌ | ⚠️ |
| Multi-serie en 1 request | ✅ **UNICO** | ❌ | ❌ |
| Documentacion oficial publica | ✅ | ✅ | ✅ |

**Cuando usar `indec` vs `bcra-macro`:**
- INDEC (IPC, EMAE, EPH, PIB) → `indec`
- Solo BCRA con cobertura completa → `bcra-macro`
- Cruzar INDEC + BCRA en un dataset → `indec`

---

## Casos de uso comunes

> **30+ recetas completas en [`references/COOKBOOK.md`](./references/COOKBOOK.md).**

```bash
# Inflacion mensual ultimos 12 meses
py scripts/fetch_indec.py ipc --last 12

# Inflacion interanual desde el indice
py scripts/fetch_indec.py series "<ID_IPC_INDICE>" --mode percent_change_a_year_ago

# Dolar diario → promedio mensual
py scripts/fetch_indec.py dolar --collapse month --aggregation avg

# Exportaciones totales por año
py scripts/fetch_indec.py series "75.3_IETG_0_M_31" --collapse year --aggregation sum --last 10

# Comparar IPC + RIPTE + Dolar (poder adquisitivo)
py scripts/fetch_indec.py series "145.3_INGNACUAL_DICI_M_38,158.1_REPTE_0_0_5,168.1_T_CAMBIOR_D_0_0_26" --last 12

# Snapshot macro
py scripts/fetch_indec.py snapshot --last 3
```

---

## Documentacion completa

| Documento | Contenido |
|-----------|-----------|
| [`references/REFERENCE.md`](./references/REFERENCE.md) | Overview general + arquitectura |
| [`references/ENDPOINTS.md`](./references/ENDPOINTS.md) | Deep dive de `/series`, `/search`, `/dump`, `/validate` |
| [`references/PARAMS.md`](./references/PARAMS.md) | Cada parametro con valores validos, defaults, ejemplos |
| [`references/REPRESENTATION_MODES.md`](./references/REPRESENTATION_MODES.md) | Las 7 transformaciones con ejemplos calculados |
| [`references/COLLAPSE_AGGREGATIONS.md`](./references/COLLAPSE_AGGREGATIONS.md) | Agregacion temporal con casos de uso |
| [`references/SERIES_CATALOG.md`](./references/SERIES_CATALOG.md) | IDs canonicos organizados por topico |
| [`references/RESPONSE_FORMAT.md`](./references/RESPONSE_FORMAT.md) | Schema JSON / CSV completo |
| [`references/DATA_SOURCES.md`](./references/DATA_SOURCES.md) | Organismos publicadores con datasets |
| [`references/COOKBOOK.md`](./references/COOKBOOK.md) | **30+ recetas listas para copy-paste** |
| [`references/LIMITATIONS_TROUBLESHOOTING.md`](./references/LIMITATIONS_TROUBLESHOOTING.md) | Limites + errores comunes + debugging |
| [`assets/known_series_ids.json`](./assets/known_series_ids.json) | Catalogo curado de IDs |
| [`assets/series_groups.json`](./assets/series_groups.json) | Bundles pre-armados por caso |
| [`assets/representation_modes.json`](./assets/representation_modes.json) | Modes con descripcion |
| [`assets/collapse_aggregations.json`](./assets/collapse_aggregations.json) | Aggregations con casos |
| [`assets/data_sources.json`](./assets/data_sources.json) | Publicadores estructurados |

---

## ⚠️ Limitaciones conocidas

> Documentacion completa de limitaciones en
> [`references/LIMITATIONS_TROUBLESHOOTING.md`](./references/LIMITATIONS_TROUBLESHOOTING.md).

### Las mas importantes

1. **Maximo 1,000 datapoints por serie por request** — para series muy largas, paginar con `--offset`.
2. **`--last` incompatible con `--sort`, `--limit`, `--offset`** — el script lo maneja automaticamente.
3. **Multi-serie con frecuencias mezcladas** — usar `--collapse` explicito para evitar surprises.
4. **Series DISCONTINUADAS** marcadas como `SERIE DISCONTINUADA` en `dataset.title` — filtrarlas cliente-side.
5. **IDs criptos** — no intentar adivinar, usar `search` o el catalogo curado.
6. **Lag del INDEC**: IPC mensual aparece ~15 dias despues, PIB trimestral ~3 meses.

### Por que esta API es MAS confiable que las demas

A diferencia de TradingView/Google Finance/BYMA (todas APIs internas):

- ✅ **API oficial publica** del Estado Argentino.
- ✅ **Documentacion oficial**: [datosgobar.github.io/series-tiempo-ar-api](https://datosgobar.github.io/series-tiempo-ar-api/)
- ✅ **Codigo abierto en GitHub**: [datosgobar/series-tiempo-ar-api](https://github.com/datosgobar/series-tiempo-ar-api)
- ✅ **Politicas de no-break ABI** — estable desde 2017+.
- ✅ Issue tracker publico.

**Podes construir productos sobre esta API con muchisima mas confianza
que sobre las APIs internas.**

---

## Referencias externas

- **Documentacion oficial:** https://datosgobar.github.io/series-tiempo-ar-api/
- **Codigo abierto (GitHub):** https://github.com/datosgobar/series-tiempo-ar-api
- **Portal datos.gob.ar:** https://datos.gob.ar
- **INDEC oficial:** https://www.indec.gob.ar
- **BCRA oficial:** https://www.bcra.gob.ar
