---
name: mae
description: "Datos de mercado del MAE (Mercado Abierto Electronico de Argentina): renta fija, cauciones, REPO, FOREX, contratos de futuro dolar (DDF), indice ARS-MAE, licitaciones primarias, comunicados institucionales, flujos de fondos para curvas. Sin API key."
license: MIT
---

# MAE — Mercado Abierto Electronico de Argentina

Skill para extraer datos de mercado mayorista del [MAE](https://www.mae.com.ar)
via su **API publica de market data** — sin API key, sin autenticacion.

El MAE es el mercado argentino mayorista donde se negocian:

- **Renta Fija** (LECAPs, BONCAPs, BOPREALes, bonos hard dollar, ONs).
- **Cauciones** (CAARS pesos, CAUSD dolares por plazo).
- **REPO / Simultaneas** (REPO, REPX, SIMU).
- **FOREX** mayorista (dolar transferencia, EUR, CNH, GBP).
- **Dolar Diferido a Fix (DDF)** — futuros de dolar mensuales.
- **Indice ARS-MAE** — referencia del dolar mayorista.
- **Licitaciones primarias** de provincias, ONs y Tesoro.

---

## ⚠️ Aviso Legal

- API publica del MAE, sin documentacion oficial. Los endpoints **pueden cambiar sin aviso**.
- Respetar terminos de uso del MAE. No hacer mas de 1 req/segundo (no documentado pero razonable).
- Los datos son **delayed** (5-15 min en intradia; T-1 en historicos).
- Para uso comercial intensivo, contactar al MAE para licencias formales.

---

## Scripts

| Script | Descripcion |
|--------|-------------|
| **[fetch_mae.py](./scripts/fetch_mae.py)** | Script principal: todos los endpoints disponibles |

---

## Uso rapido

```bash
# ── SNAPSHOTS INTRADIA ──────────────────────────────────────────────────

# Resumen top 10 de cada categoria (con grafico intradia mini)
py scripts/fetch_mae.py resumen RF       # Renta fija (LECAPs/BONCAPs lideres)
py scripts/fetch_mae.py resumen CAU      # Cauciones (CAARS/CAUSD)
py scripts/fetch_mae.py resumen FOR      # FOREX (US$ tran, EUR, etc.)
py scripts/fetch_mae.py resumen DDF      # Dolar Diferido a Fix (futuros)

# Cotizaciones COMPLETAS del dia (no solo top 10)
py scripts/fetch_mae.py datos RF         # ~289 lineas
py scripts/fetch_mae.py datos CAU        # ~3 lineas
py scripts/fetch_mae.py datos FOR        # ~14 lineas

# Volumen por categoria (Renta Fija TRD / PPT / FOREX) con share %
py scripts/fetch_mae.py volumen ARS      # En pesos
py scripts/fetch_mae.py volumen USD      # En dolares

# Indice ARS-MAE actual (PBO + PPN intradia)
py scripts/fetch_mae.py indice-ars

# ── MAPA DE PROSPECTOS ──────────────────────────────────────────────────

# Mapa de titulos por segmento/plazo/moneda
py scripts/fetch_mae.py mapa --segmento BT --plazo 001 --moneda '$'
py scripts/fetch_mae.py mapa --segmento BT --plazo 002 --moneda D
py scripts/fetch_mae.py mapa --segmento PPT --plazo 001 --moneda '$'

# ── INSTITUCIONAL ───────────────────────────────────────────────────────

# Comunicados (sin filtro: ultimos 60; con filtro: rango especifico)
py scripts/fetch_mae.py comunicados
py scripts/fetch_mae.py comunicados --desde 2026-05-05 --hasta 2026-06-05

# Calendario de licitaciones proximas
py scripts/fetch_mae.py licitaciones

# Licitaciones DETALLADAS filtradas por estado
py scripts/fetch_mae.py licitaciones-estado --estado A --desde 2026-05-05 --hasta 2026-06-05
py scripts/fetch_mae.py licitaciones-estado --estado F --desde 2026-05-05 --hasta 2026-06-05
py scripts/fetch_mae.py licitaciones-estado --estado P --desde 2026-05-05 --hasta 2026-06-05

# ── CURVAS RENTA FIJA ───────────────────────────────────────────────────

# Flujo fondos cotizaciones (precio + TIR + MD + cashflows futuros)
py scripts/fetch_mae.py flujo-fondos H   # Bonos hard dollar (AE38, etc.)
py scripts/fetch_mae.py flujo-fondos B   # BOPREALes serie 1

# ── HISTORICOS ──────────────────────────────────────────────────────────

# Historico renta fija (grid + chart)
py scripts/fetch_mae.py hist-rf --desde 2026-05-05 --hasta 2026-06-04

# Historico FOREX (por dia con detalle de cada moneda/plazo)
py scripts/fetch_mae.py hist-forex --desde 2026-05-05 --hasta 2026-06-05

# Volumen FOREX por dia (sin detalle)
py scripts/fetch_mae.py hist-forex-vol --desde 2026-05-05 --hasta 2026-06-05

# Historico cauciones agrupado por dia
py scripts/fetch_mae.py hist-cau --desde 2026-05-05 --hasta 2026-06-05

# Serie de tasas + volumen de UNA caucion especifica (titulo + plazo)
py scripts/fetch_mae.py hist-cau-vt --titulo CAARS --plazo 001 --desde 2026-05-05 --hasta 2026-06-05
py scripts/fetch_mae.py hist-cau-vt --titulo CAUSD --plazo 001 --desde 2026-05-05 --hasta 2026-06-05

# Historico REPO con detalle por rueda (REPO, REPX, SIMU)
py scripts/fetch_mae.py hist-repo --desde 2026-05-05 --hasta 2026-06-05

# Volumen y tasa PP REPO por fecha (sin detalle por rueda)
py scripts/fetch_mae.py repo-fecha --desde 2026-05-05 --hasta 2026-06-05

# Indice ARS-MAE historico (PPN al cierre por dia)
py scripts/fetch_mae.py indice-ars-hist --desde 2026-05-05 --hasta 2026-06-05

# ── COMBINADOS ──────────────────────────────────────────────────────────

# Todos los snapshots (resumen + datos + volumen + indice + comunicados + licitaciones + flujos)
py scripts/fetch_mae.py all

# ── OUTPUT ─────────────────────────────────────────────────────────────

# Guardar a archivo
py scripts/fetch_mae.py resumen RF -o resumen_rf.json
py scripts/fetch_mae.py all -o snapshot.json

# Modo silencioso (solo JSON, sin logs)
py scripts/fetch_mae.py resumen RF -q
```

---

## Endpoints disponibles

| Modo | Data | Endpoint |
|------|------|----------|
| `resumen <tipo>` | Top 10 titulos lideres + mini-grafico intradia | `/api/mercado/resumen/{RF\|CAU\|FOR\|DDF}` |
| `datos <tipo>` | TODAS las cotizaciones del dia (~289 lineas en RF) | `/api/mercado/datos/{RF\|CAU\|FOR}` |
| `volumen <moneda>` | Volumen por categoria de mercado con share % | `/api/mercado/volumen-categoria/{ARS\|USD}` |
| `mapa` | Mapa de prospectos por segmento/plazo/moneda | `/api/mercado/mapa?oTitulo={...}` |
| `comunicados` | Comunicados institucionales del MAE | `/api/institucional/comunicados[?oTitulo={...}]` |
| `licitaciones` | Calendario de licitaciones primarias proximas | `/api/mercado/licitaciones` |
| `licitaciones-estado` | Licitaciones detalladas por estado y rango | `/api/mercado/licitacionesporestado/Todos?oTitulo={...}` |
| `flujo-fondos <letra>` | Cashflows + precio + TIR + MD para curvas RF | `/api/emisiones/flujofondoscotiz/{B\|H}` |
| `hist-rf` | Historico renta fija por rango | `/api/mercado/titulo/historicorentafija?oTitulo={...}` |
| `hist-forex` | Historico FOREX por rango (con detalle) | `/api/mercado/titulo/historicoforex?oTitulo={...}` |
| `hist-forex-vol` | Solo volumen total FOREX por dia | `/api/mercado/titulo/historicoforex/volumenoperado?oTitulo={...}` |
| `hist-cau` | Historico cauciones por rango | `/api/mercado/titulo/historicocauciones?oTitulo={...}` |
| `hist-cau-vt` | Series de tasa y volumen para 1 caucion | `/api/mercado/cauciones/valorescierre/volumentasas?oTitulo={...}` |
| `hist-repo` | Historico REPO con detalle por rueda | `/api/mercado/titulo/historicorepo?oTitulo={...}` |
| `repo-fecha` | Volumen + tasaPP REPO por fecha | `/api/mercado/repo/titulosfecha?oTitulo={...}` |
| `indice-ars` | Indice ARS-MAE snapshot intradia (PBO + PPN) | `/api/mercado/indiceARS` |
| `indice-ars-hist` | Serie historica diaria del Indice ARS-MAE | `/api/mercado/titulo/indicearsmae/historico?oTitulo={...}` |
| `all` | Todos los snapshots actuales (sin historicos) | (combinado) |

**Total: 17 endpoints publicos verificados ✅**

---

## Categorias soportadas

### Tipos validos para `resumen`

| Tipo | Descripcion | Ejemplo de tickers |
|------|-------------|---------------------|
| `RF` | Renta Fija | `S12J6` (LECAP), `BPOB7` (BOPREAL), `AE38` (Bono USD step-up) |
| `CAU` | Cauciones | `CAARS $ 001`, `CAUSD D 007` |
| `FOR` | FOREX | `UST$T` (dolar transferencia mayorista), `EB$T` (Euro billete) |
| `DDF` | Dolar Diferido a Fix (futuros) | `DLR062026`, `DLR072026`, `DLR082026` |

> Cualquier otro tipo (REPO, DLR, RVA, etc.) retorna **HTTP 400**.

### Tipos validos para `datos`

Igual que `resumen` excepto:
- `DDF` retorna **HTTP 500** (no soportado).

### Estados validos para `licitaciones-estado`

| Codigo | Estado |
|--------|--------|
| `A` | Activa |
| `F` | Finalizada |
| `C` | Cancelada |
| `S` | Suspendida (suele venir vacio) |
| `P` | Programada |

> Otros codigos (`M`, `X`, `N`, `I`, `T`, `Todos`) retornan **HTTP 400**.

### Letras validas para `flujo-fondos`

| Letra | Categoria | Ejemplos |
|-------|-----------|----------|
| `H` | Hard dollar step-up | AE38, AL30, GD30 |
| `B` | BOPREALes serie 1 | BPOB7, BPOD7, BPOC7 |

> Otras letras retornan lista vacia. `C` retorna **HTTP 500**.

### Tickers validos para `hist-cau-vt`

| Ticker | Descripcion |
|--------|-------------|
| `CAARS` | Caucion en pesos |
| `CAUSD` | Caucion en dolares |
| `CAU` | Aggregated (CAARS + CAUSD) |

### Plazos comunes

| Plazo | Dias | Descripcion |
|-------|------|-------------|
| `000` | 0 | CI (Contado Inmediato) |
| `001` | 1 | 24hs |
| `002` | 2 | 48hs |
| `007` | 7 | 7 dias |

### Monedas

| Codigo | Descripcion |
|--------|-------------|
| `$` | Pesos argentinos |
| `D` | Dolar Bilateral D (similar MEP) |
| `T` | Dolar transferencia mayorista |
| `C` | Dolar Cable (CCL) |

### Segmentos comunes (mercado/mapa)

| Codigo | Descripcion |
|--------|-------------|
| `BT` | Bilateral TRD |
| `PPT` | Plazo Pesos Transferible |
| `PT` | Plazo Transferible |
| `BL` | Bilateral |
| `TX` | Tomador/Colocador |
| `RV` | Renta Variable |
| `EX` | Extranjeras (Cedears, ADRs) |

---

## Consideraciones tecnicas

### Datos devueltos por `resumen`

Cada item:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `ticker` | string | Codigo del titulo |
| `tipoEmision` | string | `TPN`, `TPP`, `ON`, `CAU`, `FOR`, `DDF` |
| `descripcion` | string | Descripcion humana |
| `plazo` | string | Codigo de plazo |
| `fechaLiquidacion` | string\|null | ISO8601 |
| `moneda` | string | `$`, `D`, `T`, `C` |
| `segmento` | string | Codigo de segmento |
| `variacion` | float | Variacion % vs cierre anterior |
| `ultimo` | float | Ultimo precio operado |
| `cantidad` | float | Cantidad nominal |
| `monto` | float | Monto efectivo |
| `datosGrafico.precios[]` | list | Serie intradia `{time: unix_ts_s, value: float}` |
| `datosGrafico.volumenes[]` | list | Serie intradia de volumenes |

### Datos devueltos por `datos`

Mismo schema que `resumen` mas:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `volumen` | float | Cantidad nominal negociada |
| `codigoSegmento` | string | Codigo corto del segmento |
| `ultimaTasa` | float | Solo cauciones/REPO (en bonos = 0) |
| `cierreAnterior` | float | Precio o tasa cierre anterior |
| `minimo`, `maximo` | float | Rango del dia |
| `openInterest` | float | Solo DDF/REPO |
| `precioCierre`, `precioApertura` | float\|null | Open/Close del dia |

> Y NO incluye `datosGrafico` (eso es exclusivo de `resumen`).

### Datos devueltos por `volumen`

| Campo | Descripcion |
|-------|-------------|
| `nombre` | Nombre corto categoria |
| `descripcion` | Descripcion larga |
| `volumen` | Volumen del dia |
| `share` | Share % dentro del grupo |
| `grupo` | `Contado`, `Monedas` |
| `moneda` | `ARS` o `USD` |
| `orden` | Orden de display |

### Datos devueltos por `licitaciones`

```json
{
  "timeZone": "UTC",
  "events": [
    {"id": -621, "title": "...", "start": "...", "end": "..."}
  ]
}
```

### Datos devueltos por `licitaciones-estado`

Cada licitacion incluye 30+ campos: `titulo`, `emisor`, `industria`, `moneda`,
`ampliableHasta`, `variableLicitar`, `montoaLicitar`, `rueda`, `modalidad`,
`liquidador`, `estado`, `tipo`, `colocador`, `observaciones`,
`monto_Adjudicado`, `sistema_Adjudicacion`, `valor_Corte`, `duration`,
`fechaModificacion`, `plazoEspecie`, `archivos[]`.

### Datos devueltos por `flujo-fondos`

Cada bono:

| Campo | Descripcion |
|-------|-------------|
| `especie` | Ticker del bono |
| `descripcion` | Descripcion humana |
| `moneda` | `D  ` (dolar) o `$` |
| `precio` | Precio actual cotizacion |
| `tir` | TIR anual (%) |
| `md` | Modified Duration (años) |
| `detalle[]` | Lista de cashflows futuros: `fechaPago`, `vr`, `vrCartera`, `cashFlow`, `renta`, `amortizacion`, `amasR` |

### Datos devueltos por `hist-cau-vt`

```json
{
  "tasa": [{"time": 1779840000, "value": 19.8849}, ...],
  "volumen": [{"time": 1779840000, "value": 3079030400000.0}, ...]
}
```

> `time` esta en **segundos UTC** (no milisegundos).

### Datos devueltos por `hist-repo`

Por dia, con `details[]` que incluye un item por rueda:

| Campo | Descripcion |
|-------|-------------|
| `rueda` | `REPO`, `REPX`, `SIMU` |
| `tasaApertura`, `ultimaTasa` | Tasa apertura / cierre del dia |
| `tasaMaximo`, `tasaMinimo` | Maximo y minimo del dia |
| `cierreAyer` | Cierre del dia anterior |
| `cantidad`, `volumen` | Cantidad nominal y volumen efectivo |
| `tasaPP` | Tasa promedio ponderada |
| `variacion` | Variacion vs cierre anterior |
| `cantOperaciones` | Numero de operaciones |
| `plazo`, `segmento` | Plazo y segmento |

### Flags adicionales

| Flag | Descripcion |
|------|-------------|
| `--desde YYYY-MM-DD` | Fecha desde (requerida en historicos y `licitaciones-estado`) |
| `--hasta YYYY-MM-DD` | Fecha hasta (requerida en historicos y `licitaciones-estado`) |
| `--segmento <COD>` | Segmento para `mapa` (default: `BT`) |
| `--plazo <COD>` | Plazo (default: `001`) |
| `--moneda <COD>` | Moneda para `mapa` (default: `$`) |
| `--estado <COD>` | Estado para `licitaciones-estado` (default: `A`) |
| `--titulo <TICKER>` | Ticker para `hist-cau-vt` (default: `CAARS`) |
| `--unit <COD>` | Unit para `repo-fecha` (ignorado por la API; default: `USD`) |
| `-o archivo.json` | Guardar output a archivo JSON |
| `-q` / `--quiet` | Modo silencioso (solo JSON, sin logs) |

### Rate limiting

No hay rate limiting documentado. Se recomienda:
- Minimo **0.3 segundos** entre requests.
- El modo `all` usa `time.sleep(0.3)` entre cada llamada automaticamente.

### Encoding

Algunos campos texto (titulos de licitaciones, comentarios) tienen
caracteres latin-1 que se muestran como `?` en consola Windows pero se
salvan bien con `json.dumps(..., ensure_ascii=False)` en archivos UTF-8.

### Manejo de errores

| Status | Causas tipicas |
|--------|----------------|
| 400 | Tipo / estado / parametro invalido. Verificar valores soportados arriba. |
| 404 | Endpoint inexistente. Las paths solo aceptan lo listado en este SKILL. |
| 500 | Combinacion no soportada (ej: `datos/DDF`, `flujo-fondos/C`). |

El script captura `HTTPError` y muestra el body con el mensaje de error.

---

## Estructura del skill

```
skills/mae/
├── SKILL.md                          # Este archivo (guia rapida)
├── references/
│   └── REFERENCE.md                  # Documentacion completa de todos los endpoints
└── scripts/
    └── fetch_mae.py                  # Script principal
```

---

> **Documentacion detallada:** Consultar [references/REFERENCE.md](./references/REFERENCE.md)
> para documentacion exhaustiva de cada endpoint, schemas JSON, ejemplos,
> codigos de segmentos/plazos/monedas/ruedas y consideraciones tecnicas.
