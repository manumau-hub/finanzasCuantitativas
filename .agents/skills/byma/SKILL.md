---
name: byma
description: "Datos de mercado de BYMA (Bolsas y Mercados Argentinos) via API publica: paneles de acciones lideres, CEDEARs, bonos soberanos, LECAPs/BONCAPs, ONs corporativas, cauciones, opciones y SENEBI. Historicos OHLCV de instrumentos e indices (MERVAL, BURCAP). Ficha tecnica de bonos con cronograma de amortizacion. Sin API key."
license: MIT
---

# BYMA — Bolsas y Mercados Argentinos

Skill para extraer datos de mercado de [BYMA](https://www.byma.com.ar)
via su **API publica de market data** (`open.bymadata.com.ar`) — sin API
key, sin autenticacion.

BYMA es la bolsa principal de Argentina (sucesora del Merval) donde se
negocian:

- **Acciones lideres** (panel de 20 simbolos del MERVAL).
- **CEDEARs** (~1143 unicos x 2 settlements).
- **Bonos publicos soberanos** + LECAPs + BONCAPs (~104 unicos x 6 variantes).
- **Obligaciones Negociables (ON)** corporativas (~2117 items).
- **SENEBI ON** (segmento bilateral, ~3160 items).
- **Cauciones** (133 items, formato `DOLAR-DDMM-U-CT-USD`).
- **Opciones** (~429 items con strike, OI, vencimiento).
- **Indices**: S&P MERVAL (`M`), BURCAP (`G`).
- **Historicos OHLCV** diarios/semanales/mensuales para todos los instrumentos.
- **Ficha tecnica de bonos** (forma de amortizacion, intereses step-up, ISIN, ley aplicable, emisor).

---

## ⚠️ Aviso Legal

- API publica de BYMA, sin documentacion oficial. Los endpoints **pueden cambiar sin aviso**.
- Respetar terminos de uso de BYMA. No hacer mas de 1 req/segundo.
- Los datos son **delayed** (~15 min tipico de mercado argentino).
- Para uso comercial intensivo, contactar BYMA para licencias oficiales.

---

## 🔒 Nota sobre certificado SSL

BYMA presenta un certificado SSL cuya CA intermedia no esta incluida en
el bundle `certifi` estandar de Python. Esto causa:

```
SSLError: CERTIFICATE_VERIFY_FAILED
```

**El script usa `verify=False`** — la conexion sigue siendo TLS-encriptada
pero se omite la validacion de cadena. Es el patron estandar de las
librerias publicas de BYMA (`pyhomebroker`, `bymadata`, etc.).

Si preferis no usar `verify=False`, podes instalar el cert intermedio de
BYMA en tu trust store del sistema.

---

## Scripts

| Script | Descripcion |
|--------|-------------|
| **[fetch_byma.py](./scripts/fetch_byma.py)** | Script principal: todos los endpoints disponibles |

---

## Uso rapido

```bash
# ── PANELES (POST) ────────────────────────────────────────────────────

# Panel lideres: 20 acciones MERVAL x 2 settlements (40 items)
py scripts/fetch_byma.py panel leading-equity
py scripts/fetch_byma.py panel leading-equity --t0    # solo CI (T+0)
py scripts/fetch_byma.py panel leading-equity --t1    # solo 24hs (T+1)

# Panel CEDEARs (~2000 items, lista directa)
py scripts/fetch_byma.py panel cedears

# Panel bonos publicos (1018 items, paginado a 189 por defecto)
py scripts/fetch_byma.py panel public-bonds
py scripts/fetch_byma.py panel public-bonds --all     # trae los 1018 en una llamada

# Panel ON corporativas (~2117 items, lista directa)
py scripts/fetch_byma.py panel on

# Panel cauciones (~133 items)
py scripts/fetch_byma.py panel cauciones

# Panel SENEBI ON (3160 items, paginado)
py scripts/fetch_byma.py panel senebi-on
py scripts/fetch_byma.py panel senebi-on --all        # trae los 3160 en una llamada

# Panel opciones (~429 items, con strike, OI, vencimiento)
py scripts/fetch_byma.py panel options

# ── HISTORICOS OHLCV (GET) ────────────────────────────────────────────

# Historico de un instrumento — formato simbolo: "TICKER 24HS"
py scripts/fetch_byma.py historico "GGAL 24HS"
py scripts/fetch_byma.py historico "ALUA 24HS"
py scripts/fetch_byma.py historico "AAPL 24HS"        # CEDEAR ARS
py scripts/fetch_byma.py historico "AAPLD 24HS"       # CEDEAR USD
py scripts/fetch_byma.py historico "AL30 24HS"        # Bono ARS
py scripts/fetch_byma.py historico "AL30D 24HS"       # Bono USD
py scripts/fetch_byma.py historico "AL30C 24HS"       # Bono CCL
py scripts/fetch_byma.py historico "GD30 24HS"
py scripts/fetch_byma.py historico "TZX26 24HS"       # BONCAP
py scripts/fetch_byma.py historico "TY30P 24HS"       # BONCAP

# Con rango de fechas (default: ultimos 30 dias)
py scripts/fetch_byma.py historico "GGAL 24HS" --desde 2024-05-15 --hasta 2026-06-05

# Resolutions: D (diario), W (semanal), M (mensual)
py scripts/fetch_byma.py historico "GGAL 24HS" --resolution W
py scripts/fetch_byma.py historico "GGAL 24HS" --resolution M

# ── INDICES ────────────────────────────────────────────────────────────

# Historico del S&P MERVAL
py scripts/fetch_byma.py indice M
py scripts/fetch_byma.py indice M --desde 2025-01-01 --hasta 2026-06-05

# Historico del BURCAP
py scripts/fetch_byma.py indice G

# ── FICHA TECNICA DE BONOS ─────────────────────────────────────────────

# Ficha tecnica completa: forma de amortizacion, intereses, ISIN, ley, emisor
py scripts/fetch_byma.py bond-info AE38            # Bono soberano USD 2038 step-up
py scripts/fetch_byma.py bond-info AL30            # Bono soberano USD 2030 ley local
py scripts/fetch_byma.py bond-info GD30            # Bono soberano USD 2030 ley NY
py scripts/fetch_byma.py bond-info AE38C           # Variante CCL (misma ficha)
py scripts/fetch_byma.py bond-info AE38D           # Variante USD MEP (misma ficha)
py scripts/fetch_byma.py bond-info BPOA7           # BOPREAL Serie 1 A
py scripts/fetch_byma.py bond-info TY30P           # BONCAP
py scripts/fetch_byma.py bond-info TZX26           # BONCAP CER
py scripts/fetch_byma.py bond-info S237Q           # LECAP
py scripts/fetch_byma.py bond-info SBC1C           # ON corporativa

# ── COMBINADO ──────────────────────────────────────────────────────────

# Snapshot de todos los paneles + MERVAL + BURCAP
py scripts/fetch_byma.py all

# ── OUTPUT ─────────────────────────────────────────────────────────────

# Guardar a archivo JSON
py scripts/fetch_byma.py panel leading-equity -o leading.json
py scripts/fetch_byma.py all -o snapshot_byma.json

# Modo silencioso (solo JSON, sin logs)
py scripts/fetch_byma.py panel cauciones -q
```

---

## Endpoints disponibles

| Modo | Data | Endpoint |
|------|------|----------|
| `panel leading-equity` | Top 20 acciones MERVAL x 2 settlements (40 items) | `POST /leading-equity` |
| `panel cedears` | CEDEARs (~2000 items) | `POST /cedears` |
| `panel public-bonds` | Bonos soberanos + LECAPs/BONCAPs (~1018 items) | `POST /public-bonds` |
| `panel on` | ONs corporativas (~2117 items) | `POST /negociable-obligations` |
| `panel cauciones` | Cauciones (~133 items) | `POST /cauciones` |
| `panel senebi-on` | SENEBI ONs (~3160 items, paginado) | `POST /senebi-obligaciones-negociables` |
| `panel options` | Opciones (~429 items) | `POST /options` |
| `historico <SYM>` | OHLCV diario/semanal/mensual de un instrumento | `GET /chart/historical-series/history?symbol={...}` |
| `indice <COD>` | OHLCV de un indice (M=MERVAL, G=BURCAP) | `GET /chart/index-historical-series/history?symbol={...}` |
| `bond-info <TICKER>` | Ficha tecnica de bono/LECAP/BONCAP/ON (amortizacion, intereses, ISIN, emisor) | `POST /bnown/fichatecnica/especies/general` |
| `all` | Snapshot de todos los paneles + indices | (combinado) |

**Total: 10 endpoints publicos verificados ✅** (8 POST + 2 historicos GET).

### Base URL

```
https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free
```

---

## Convenciones de simbolos

### Historicos: formato `TICKER 24HS`

⚠️ **TODOS los historicos requieren el sufijo ` 24HS`** (con espacio).
Sin sufijo retorna HTTP 400. El sufijo `CI` tambien retorna 400 (no
soportado). `48HS` retorna 200 con 0 puntos.

| Tipo | Ejemplo |
|------|---------|
| Accion | `GGAL 24HS`, `ALUA 24HS`, `YPFD 24HS` |
| CEDEAR ARS | `AAPL 24HS`, `MSFT 24HS` |
| CEDEAR USD | `AAPLD 24HS`, `MSFTD 24HS` |
| Bono soberano ARS | `AL30 24HS`, `GD30 24HS`, `AE38 24HS` |
| Bono soberano USD MEP | `AL30D 24HS`, `GD30D 24HS` |
| Bono soberano CCL | `AL30C 24HS`, `GD30C 24HS` |
| LECAP/BONCAP | `TY30P 24HS`, `TZX26 24HS` |

### Bonos: convencion de sufijos por moneda

| Sufijo | Variante | Ejemplo |
|--------|----------|---------|
| (sin) | ARS — paridad en pesos | `AL30` |
| `C` | CCL (Contado con Liquidacion / EXT) | `AL30C` |
| `D` | USD MEP | `AL30D` |
| `X`, `Y`, `Z` | otras variantes (intra-day, settlement alt.) | `AL30X` |

### Indices conocidos

| Codigo | Indice |
|--------|--------|
| `M` | S&P MERVAL |
| `G` | BURCAP |

Otros codigos (A, B, V, etc.) son aceptados pero retornan series con
todos ceros — probablemente indices deprecated.

---

## Filtros comunes en POST paneles

| Filtro | Descripcion |
|--------|-------------|
| `T0=true` | Solo `settlementType=1` (CI / Contado Inmediato) |
| `T1=true` | Solo `settlementType=2` (24hs) |
| `T2=true` | Solo `settlementType=3` (48hs — practicamente vacio) |
| `page_size=5000` | Trae todo el dataset en una sola llamada (recomendado para `public-bonds` y `senebi-on`) |

⚠️ El parametro `page` (numero de pagina) **es ignorado por la API** —
siempre devuelve pagina 1. Workaround: usar `page_size` grande o flag `--all`.

---

## Consideraciones tecnicas

### Datos devueltos por `panel` (todos)

Cada item incluye:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Ticker BYMA. |
| `settlementType` | string | `"1"` (CI) o `"2"` (24hs). |
| `securityType` | string | `CS` (Common Stock), `CD` (CEDEAR), `GO` (Government Obligation), `CORP` (ON), `QS` (Caucion), `OPT` (Option). |
| `denominationCcy` | string | `ARS`, `USD`, `EXT`. |
| `market` | string | `BYMA` o `SENEBI`. |
| `trade` | float | Ultimo precio operado. |
| `closingPrice` | float | Cierre del dia. |
| `settlementPrice` | float | Precio de settlement. |
| `openingPrice`, `tradingHighPrice`, `tradingLowPrice` | float | OHL del dia. |
| `previousClosingPrice`, `previousSettlementPrice` | float | Cierre / settlement anterior. |
| `imbalance` | float | Variacion % vs anterior (decimal: -0.0098 = -0.98%). |
| `volume`, `tradeVolume` | float | Volumen nominal. |
| `volumeAmount` | float | Monto efectivo en moneda. |
| `vwap` | float | Volume-Weighted Average Price. |
| `bidPrice`, `offerPrice` | float | Mejor bid/offer (0 fuera de horario). |
| `quantityBid`, `quantityOffer` | float | Cantidades de bid/offer. |
| `numberOfOrders` | int | Numero total de ordenes del dia. |
| `openInterest` | float | Interes abierto (real en opciones/cauciones; 0 en acciones). |
| `tickDirection` | int | -1 / 0 / +1 (downtick / unchanged / uptick). |
| `tradeHour` | string | Hora del ultimo trade. |

### Campos extra en bonos / ONs / cauciones / opciones

| Campo | Descripcion |
|-------|-------------|
| `maturityDate` | Fecha de vencimiento (ISO `YYYY-MM-DD`). |
| `daysToMaturity` | Dias hasta vencimiento. |
| `underlyingSymbol` | Underlying (solo cauciones y opciones). |
| `optionType` | `CALL` o `PUT` (solo opciones). |

### Datos devueltos por `historico` e `indice`

```json
{
  "s": "ok",
  "t": [unix_seconds, ...],
  "o": [opens, ...],
  "h": [highs, ...],
  "l": [lows, ...],
  "c": [closes, ...],
  "v": [volumes, ...]
}
```

| Campo | Descripcion |
|-------|-------------|
| `s` | Status: `"ok"`, `"no_data"`, `"error"`. |
| `t[]` | Timestamps unix UTC SECONDS (no millis). |
| `o[]`, `h[]`, `l[]`, `c[]` | OHLC alineados por indice. |
| `v[]` | Volumen (suele ser 0 en indices). |

### Datos devueltos por `bond-info`

Devuelve `{content, data, empty, upgrade}` donde `data[0]` (cuando existe)
contiene la ficha tecnica del bono. Para acciones, opciones y tickers
inexistentes: `data: []` y `empty: true`.

Campos del `data[0]`:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `ley` | string | Jurisdiccion aplicable: `Nacional`, `Extranjera`, `Nueva York`, `Inglaterra`. Critico para distinguir AL30 (ley local) de GD30 (ley NY). |
| `formaAmortizacion` | string | **TEXTO PLANO** con el cronograma de amortizacion (numero de cuotas, periodicidad, fechas, %). Para bullet: `"Al vencimiento"`. |
| `interes` | string | **TEXTO PLANO** con esquema de devengo de intereses. Para step-up describe cada tramo de tasa. Para CER describe el ajuste por inflacion. |
| `denominacionMinima` | int | Denominacion minima de emision. |
| `fechaEmision` | string | `YYYY-MM-DD HH:MM:SS.f`. |
| `fechaVencimiento` | string | `YYYY-MM-DD HH:MM:SS.f`. |
| `fechaDevenganIntereses` | string | Fecha inicio devengo (suele estar vacia). |
| `codigoIsin` | string | ISIN del instrumento. |
| `tipoEspecie` | string | `Titulos Publicos`, `Obligaciones Negociables`, `Letras del Tesoro`. |
| `tipoObligacion` | string | Clasificacion regulatoria: `Valores Publicos Nacionales`, `Provinciales`, `Corporativos`. |
| `tipoGarantia` | string | `Comun`, etc. |
| `default` | string | Estado de default (vacio si esta al dia). |
| `montoNominal` | int | Monto nominal total emitido. |
| `montoResidual` | int | Monto residual actual (post-amortizaciones). |
| `denominacion` | string | Nombre oficial completo del bono. |
| `insType` | string | `BOND`. |
| `paisLey` | string | Pais de ley aplicable. |
| `moneda` | string | `Dolares`, `Pesos`, `Pesos Ajustables por CER`, `Dolar Linked`. |
| `emisor` | string | `Gobierno Nacional`, `Provincia de Buenos Aires`, `YPF S.A.`, etc. |

### Diferencia entre paneles `dict` y `list`

| Panel | Tipo response | Estructura |
|-------|---------------|------------|
| `leading-equity`, `public-bonds`, `senebi-on` | dict | `{content: {page_number, page_count, page_size, total_elements_count}, data: [...], empty, upgrade}` |
| `cedears`, `on`, `cauciones`, `options` | list | `[item, item, ...]` directo |

### Flags adicionales

| Flag | Descripcion |
|------|-------------|
| `--all` | Forza `page_size=5000` para traer todo en una sola llamada |
| `--t0` | Solo settlementType=1 (CI) |
| `--t1` | Solo settlementType=2 (24hs) |
| `--page N` | Numero de pagina (ignorado por la API — usar `--all`) |
| `--page-size N` | Items por pagina (default: 200) |
| `--desde YYYY-MM-DD` | Fecha desde (historicos) |
| `--hasta YYYY-MM-DD` | Fecha hasta (historicos) |
| `--resolution X` | `D`, `W`, `M` (default: `D`) |
| `-o archivo.json` | Guardar output a archivo |
| `-q` / `--quiet` | Modo silencioso (solo JSON) |

### Rate limiting

No hay rate limiting documentado. Recomendado:
- Minimo **0.3 segundos** entre requests.
- El modo `all` usa `time.sleep(0.3)` automaticamente.

### Manejo de errores

| Status | Causas tipicas |
|--------|----------------|
| 400 | Simbolo invalido (sin `24HS`, ticker desconocido) |
| 401 | Endpoint inexistente (BYMA usa 401 generico, no 404) |
| 415 | Content-Type erroneo (POST debe ser `application/json`) |
| 500 | Error interno de BYMA |

### Conversion de fechas

```python
from datetime import datetime, timezone
# Unix seconds -> datetime
dt = datetime.fromtimestamp(ts, tz=timezone.utc)
# datetime -> Unix seconds
ts = int(datetime(2026, 6, 5, tzinfo=timezone.utc).timestamp())
```

---

## Estructura del skill

```
skills/byma/
├── SKILL.md                          # Este archivo (guia rapida)
├── references/
│   └── REFERENCE.md                  # Documentacion completa de todos los endpoints
└── scripts/
    └── fetch_byma.py                 # Script principal
```

---

> **Documentacion detallada:** Consultar [references/REFERENCE.md](./references/REFERENCE.md)
> para documentacion exhaustiva de cada endpoint, schemas JSON, codigos
> de settlementType/securityType, manejo del cert SSL, paginacion y
> consideraciones tecnicas.
