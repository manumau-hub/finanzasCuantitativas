# BYMA — Referencia Completa de la API

> **BYMA** = Bolsas y Mercados Argentinos. Bolsa principal de Argentina —
> sucesor del Merval. Negocia acciones, CEDEARs, bonos soberanos y
> corporativos (ON), opciones, cauciones y operaciones SENEBI (Sistema
> Electronico de Negociacion Bilateral).
>
> Esta documentacion cubre la API publica de market data expuesta en
> `open.bymadata.com.ar` (sin API key, sin autenticacion).

---

## Indice

1. [Resumen de endpoints](#1-resumen-de-endpoints)
2. [Convenciones de la API](#2-convenciones-de-la-api)
3. [Manejo del certificado SSL](#3-manejo-del-certificado-ssl)
4. [Panel — Leading Equity](#4-panel--leading-equity)
5. [Panel — CEDEARs](#5-panel--cedears)
6. [Panel — Public Bonds (Soberanos + LECAPs)](#6-panel--public-bonds-soberanos--lecaps)
7. [Panel — Obligaciones Negociables (ON)](#7-panel--obligaciones-negociables-on)
8. [Panel — Cauciones](#8-panel--cauciones)
9. [Panel — SENEBI Obligaciones Negociables](#9-panel--senebi-obligaciones-negociables)
10. [Panel — Opciones](#10-panel--opciones)
11. [Historico — Instrumentos](#11-historico--instrumentos)
12. [Historico — Indices](#12-historico--indices)
13. [Bond Info — Ficha tecnica de bonos / ONs](#13-bond-info--ficha-tecnica-de-bonos--ons)
14. [Codigos: settlementType, securityType, securitySubType, market](#14-codigos-settlementtype-securitytype-securitysubtype-market)
15. [Paginacion: limitaciones y workaround](#15-paginacion-limitaciones-y-workaround)
16. [Manejo de errores](#16-manejo-de-errores)
17. [Consideraciones tecnicas](#17-consideraciones-tecnicas)

---

## 1. Resumen de endpoints

| # | Modo CLI | Endpoint | Metodo | Output |
|---|----------|----------|--------|--------|
| 1 | `panel leading-equity` | `/leading-equity` | POST | dict {content, data[]} 40 items |
| 2 | `panel cedears` | `/cedears` | POST | list ~2000 items |
| 3 | `panel public-bonds` | `/public-bonds` | POST | dict {content, data[]} 1018 items |
| 4 | `panel on` | `/negociable-obligations` | POST | list ~2117 items |
| 5 | `panel cauciones` | `/cauciones` | POST | list ~133 items |
| 6 | `panel senebi-on` | `/senebi-obligaciones-negociables` | POST | dict {content, data[]} 3160 items |
| 7 | `panel options` | `/options` | POST | list ~429 items |
| 8 | `historico <SYM>` | `/chart/historical-series/history?symbol=...` | GET | dict {s, t[], o[], h[], l[], c[], v[]} |
| 9 | `indice <COD>` | `/chart/index-historical-series/history?symbol=...` | GET | dict {s, t[], o[], h[], l[], c[], v[]} |
| 10 | `bond-info <TICKER>` | `/bnown/fichatecnica/especies/general` | POST | dict {content, data[ficha]} |

**Total: 10 endpoints publicos verificados ✅** (8 POST + 2 historicos GET).

### Base URL

```
https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free
```

---

## 2. Convenciones de la API

### Headers

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
```

### POST body

Todos los endpoints POST aceptan body JSON. Payload minimo: `{}`.

Campos opcionales comunes en TODOS los paneles:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `page` | int | Numero de pagina, 1-indexed. **NOTA: la API la ignora — siempre devuelve pagina 1**. Ver seccion 14. |
| `page_size` | int | Items por pagina. Default: 189. Maximo observado: 5000+. |
| `T0` | bool | Filtra solo `settlementType = "1"` (CI / Contado Inmediato). |
| `T1` | bool | Filtra solo `settlementType = "2"` (24hs). |
| `T2` | bool | Filtra solo `settlementType = "3"` (48hs). **Devuelve vacio** (no se negocia). |

`T0 || T1` activan filtros; cuando ambos estan en `true` o en `false`, no se filtra.

### GET params

Los GET (historicos) usan query string:

| Param | Descripcion |
|-------|-------------|
| `symbol` | Simbolo (formato especifico — ver secciones 11/12). |
| `resolution` | Resolucion: `D` (diaria), `W` (semanal), `M` (mensual). |
| `from`, `to` | Timestamps Unix en SEGUNDOS (UTC). |

### Formato de fechas

- En GET params: `from` y `to` son **unix timestamp en segundos UTC** (no milisegundos).
- En responses: timestamps unix UTC seconds en `t[]`. Fechas ISO en `maturityDate` (`YYYY-MM-DD`).

### Conversion

```python
from datetime import datetime, timezone
ts = int(datetime(2026, 6, 5, tzinfo=timezone.utc).timestamp())
# Inverso:
dt = datetime.fromtimestamp(ts, tz=timezone.utc)
```

---

## 3. Manejo del certificado SSL

BYMA presenta un certificado SSL cuya CA intermedia no esta incluida en
los bundles estandar de Python (`certifi`). Esto causa:

```
SSLError: CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate
```

**Workaround usado:** `verify=False` en `requests.get/post`.

```python
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.post(url, json=payload, verify=False)
```

**Por que es razonable aqui:**

1. La data es **publica** — no se envian credenciales.
2. La conexion sigue siendo TLS-encrypted (solo se omite la validacion de cadena).
3. Es el patron estandar usado por todas las librerias publicas de BYMA
   (`pyhomebroker`, `bymadata`, etc.).
4. El usuario autorizo explicitamente esta excepcion.

Alternativa mas segura (no usada): instalar el cert intermedio de BYMA en
el trust store del sistema. Mas frecuente que falle si BYMA rota el cert.

---

## 4. Panel — Leading Equity

**Endpoint:** `POST /leading-equity`

Panel de **20 acciones lideres** del MERVAL × 2 settlements (CI + 24hs) = 40 items.

### Body

```json
{}                       // todos los settlements
{"T0": true}             // solo CI (20 items)
{"T1": true}             // solo 24hs (20 items)
{"page": 1, "page_size": 100}
```

### Response

```json
{
  "content": {
    "page_number": 1,
    "page_count": 1,
    "page_size": 189,
    "total_elements_count": 40
  },
  "data": [
    {
      "tradeVolume": 39310,
      "symbol": "ALUA",
      "imbalance": -0.0098,
      "previousSettlementPrice": 1012,
      "offerPrice": 0,
      "openInterest": 0,
      "vwap": 1018.5664716,
      "description": "",
      "numberOfOrders": 210,
      "openingPrice": 1025,
      "tickDirection": 0,
      "securityDesc": "",
      "securitySubType": "M",
      "previousClosingPrice": 1012,
      "settlementType": "1",
      "quantityOffer": 0,
      "tradingHighPrice": 1026,
      "denominationCcy": "ARS",
      "bidPrice": 0,
      "tradingLowPrice": 998,
      "market": "BYMA",
      "volumeAmount": 40039848,
      "volume": 39310,
      "trade": 1002,
      "tradeHour": "16:35:24",
      "securityType": "CS",
      "closingPrice": 1002,
      "settlementPrice": 1002,
      "quantityBid": 0
    }
  ],
  "empty": false,
  "upgrade": false
}
```

### Simbolos del panel (20)

`ALUA`, `BBAR`, `BMA`, `BYMA`, `CEPU`, `COME`, `CRES`, `ECOG`, `EDN`,
`GGAL`, `LOMA`, `METR`, `PAMP`, `SUPV`, `TGNO4`, `TGSU2`, `TRAN`, `TXAR`,
`VALO`, `YPFD`.

### Campos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Ticker BYMA del instrumento. |
| `settlementType` | string | `"1"` (CI) o `"2"` (24hs). |
| `securityType` | string | `CS` (Common Stock). |
| `securitySubType` | string | `M` (Merval — panel general). |
| `denominationCcy` | string | `ARS`, `USD`, `EXT`. |
| `market` | string | `BYMA`. |
| `trade` | float | Ultimo precio operado. |
| `closingPrice` | float | Cierre del dia. |
| `settlementPrice` | float | Precio de settlement. |
| `openingPrice`, `tradingHighPrice`, `tradingLowPrice` | float | OHL del dia. |
| `previousClosingPrice` | float | Cierre del dia anterior. |
| `previousSettlementPrice` | float | Settlement del dia anterior. |
| `imbalance` | float | Variacion % vs anterior (formato decimal: -0.0098 = -0.98%). |
| `volume` | float | Volumen nominal del dia. |
| `tradeVolume` | float | Volumen ejecutado (puede diferir de `volume` en algunos casos). |
| `volumeAmount` | float | Monto efectivo en moneda. |
| `vwap` | float | Volume-Weighted Average Price. |
| `bidPrice`, `offerPrice` | float | Mejor bid/offer actual (0 fuera de horario). |
| `quantityBid`, `quantityOffer` | float | Cantidades de mejor bid/offer. |
| `numberOfOrders` | int | Numero total de ordenes del dia. |
| `openInterest` | float | Interes abierto (0 en acciones, real en opciones/cauciones). |
| `tickDirection` | int | -1 / 0 / +1 (downtick / unchanged / uptick). |
| `tradeHour` | string | Hora del ultimo trade (`HH:MM:SS`). |

---

## 5. Panel — CEDEARs

**Endpoint:** `POST /cedears`

CEDEARs (Certificados de Deposito Argentinos) listados en BYMA.
**~1143 tickers unicos × 2 settlements** = 2000 items.

### Body

```json
{}                                  // todos
{"T0": true}                        // solo CI
{"T1": true}                        // solo 24hs
{"page_size": 5000}                 // garantia de traer todo
```

### Response

**list directa** (no envuelve en `{content, data}` como leading-equity).

### Schema

Mismo schema que leading-equity, excepto:

| Campo | Diferencia |
|-------|------------|
| `securityType` | `CD` (CEDEAR). |
| `securitySubType` | (vacio en CEDEARs). |
| `denominationCcy` | `ARS`, `USD`, `EXT`. |

### Convencion de tickers

Los CEDEARs tienen variantes por moneda:

| Sufijo | Moneda | Ejemplo |
|--------|--------|---------|
| (sin sufijo) | ARS | `AAPL` |
| `C` | Caucionable? (CCL?) | `AAPLC` |
| `D` | USD MEP | `AAPLD` |

> Esto suma 3 tickers x 2 settlements = 6 items por underlying en muchos casos.

---

## 6. Panel — Public Bonds (Soberanos + LECAPs)

**Endpoint:** `POST /public-bonds`

Bonos soberanos nacionales + LECAPs + BONCAPs. **~104 unicos × 6 variantes** = 1018 items.

### Body

```json
{"page_size": 2000}              // recomendado para traer todo
{"T0": true}                     // solo CI (506 items)
{"T1": true}                     // solo 24hs (512 items)
```

### Response

```json
{
  "content": {...},
  "data": [
    {
      "tradeVolume": 5033350,
      "symbol": "AE38",
      "imbalance": -0.0022,
      "previousSettlementPrice": 119400,
      "offerPrice": 0,
      "openInterest": 0,
      "vwap": 119789.7606008,
      "description": "",
      "numberOfOrders": 1551,
      "openingPrice": 119320,
      "tickDirection": -1,
      "securityDesc": "",
      "securitySubType": "B",
      "maturityDate": "2038-01-09",
      "previousClosingPrice": 119400,
      "settlementType": "1",
      "quantityOffer": 0,
      "tradingHighPrice": 120070,
      "denominationCcy": "ARS",
      "bidPrice": 0,
      "tradingLowPrice": 118850,
      "market": "BYMA",
      "volumeAmount": 6029437915.2,
      "volume": 5033350,
      "trade": 119130,
      "daysToMaturity": 4237,
      "tradeHour": "16:50:01",
      "securityType": "GO",
      "closingPrice": 119130,
      "settlementPrice": 119130,
      "quantityBid": 0
    }
  ]
}
```

### Campos adicionales vs acciones

| Campo | Descripcion |
|-------|-------------|
| `maturityDate` | Fecha de vencimiento del bono (ISO `YYYY-MM-DD`). |
| `daysToMaturity` | Dias hasta vencimiento. |
| `securityType` | `GO` (Government Obligation). |
| `securitySubType` | `B` (Bond) — comun en todos. |
| `denominationCcy` | `ARS`, `USD`, `EXT`. |

### Convencion de tickers — bonos hard dollar

| Sufijo | Variante | Ejemplo |
|--------|----------|---------|
| (sin) | ARS (paridad en pesos) | `AL30`, `GD30`, `AE38` |
| `C` | EXT (CCL) | `AL30C` |
| `D` | USD MEP | `AL30D` |
| `X`, `Y`, `Z` | otras variantes (intra-day, settlements alternativos) | `AL30X` |

### LECAPs y BONCAPs

Identificables por prefijo:

- `S*` (5 chars): LECAPs — ej `S237Q`, `SA24D`, `SBC1C`
- `T*` (5 chars): BONCAPs — ej `T30A7`, `T15E7`, `T2X7`

> No todos los simbolos LECAP/BONCAP tienen historico disponible. Algunos
> antiguos (S31E6) retornan 0 puntos.

---

## 7. Panel — Obligaciones Negociables (ON)

**Endpoint:** `POST /negociable-obligations`

Obligaciones Negociables corporativas (bonos corporativos). **~2117 items**.

### Body

```json
{}
{"page_size": 5000}
```

### Response

**list directa** (no envuelve).

### Campos especificos

- `securityType` = `CORP`
- `securitySubType` = (vacio o `B`)
- Misma estructura que public-bonds (incluye `maturityDate`, `daysToMaturity`).

### Convencion de tickers

- Acortados a ~5 chars con letras de variante (D, C, O, X, etc.)
- Ejemplos: `SBC1C`, `T641D`, `T661O`

---

## 8. Panel — Cauciones

**Endpoint:** `POST /cauciones`

Cauciones (prestamos colateralizados de muy corto plazo) y operaciones a plazo. **~133 items**.

### Body

```json
{}
```

### Response

**list directa**.

### Schema

```json
{
  "tradeVolume": 0.0,
  "symbol": "DOLAR-0107-U-CT-USD",
  "imbalance": 0.0,
  "previousSettlementPrice": 0.03,
  "offerPrice": 0.0,
  "openInterest": 0.0,
  "vwap": 0.0,
  "description": "",
  "numberOfOrders": 0,
  "openingPrice": 0.0,
  "tickDirection": -1,
  "underlyingSymbol": "DOLAR",
  "securityDesc": "",
  "securitySubType": "",
  "maturityDate": "2026-07-01",
  "previousClosingPrice": 0.03,
  "settlementType": "1",
  "quantityOffer": 0.0,
  "tradingHighPrice": 0.0,
  "denominationCcy": "USD",
  "bidPrice": 0.0,
  "tradingLowPrice": 0.0,
  "market": "BYMA",
  "volumeAmount": 0.0,
  "volume": 0.0,
  "trade": 0.0,
  "daysToMaturity": 27,
  "securityType": "QS",
  "closingPrice": 0.03,
  "settlementPrice": 0,
  "quantityBid": 0.0
}
```

### Convencion de tickers

`{UNDERLYING}-{DDMM}-U-CT-{CCY}` — ej `DOLAR-0107-U-CT-USD`:
- `DOLAR` = activo subyacente.
- `0107` = vencimiento (1 de Julio).
- `U-CT` = identificador del tipo.
- `USD` = moneda.

### Campos especificos

- `underlyingSymbol` = activo subyacente (`DOLAR`).
- `securityType` = `QS` (Caucion).
- `maturityDate` + `daysToMaturity` = vencimiento.
- La cotizacion (`trade`, `closingPrice`, etc.) esta en formato de tasa o
  precio segun el instrumento (cauciones suelen cotizar en tasa o factor).

---

## 9. Panel — SENEBI Obligaciones Negociables

**Endpoint:** `POST /senebi-obligaciones-negociables`

ONs negociadas en el segmento SENEBI (Sistema Electronico de Negociacion
Bilateral) — operaciones bilaterales reportadas a BYMA. **~3160 items**.

### Body

```json
{"page_size": 5000}              // recomendado
{"T0": true}                     // solo CI (1505 items)
{"T1": true}                     // solo 24hs (1655 items)
```

### Response

Envuelve en `{content, data}` igual que leading-equity.

### Schema

```json
{
  "symbol": "A11LD.SB",
  "tradeVolume": 0,
  "imbalance": 0,
  "previousSettlementPrice": 0,
  "offerPrice": 0,
  "vwap": 0,
  "description": "",
  "numberOfOrders": 0,
  "openingPrice": 0,
  "tickDirection": 0,
  "securityDesc": "",
  "securitySubType": "",
  "maturityDate": "2028-03-31",
  "previousClosingPrice": 0,
  "settlementType": "1",
  "quantityOffer": 0,
  "tradingHighPrice": 0,
  "denominationCcy": "EXT",
  "bidPrice": 0,
  "tradingLowPrice": 0,
  "market": "SENEBI",
  "volumeAmount": 0,
  "volume": 0,
  "trade": 0,
  "daysToMaturity": 666,
  "securityType": "CORP",
  "closingPrice": 0,
  "settlementPrice": 0,
  "quantityBid": 0
}
```

### Diferencias vs `panel on`

- `market` = `SENEBI` (en vez de `BYMA`).
- Sufijo `.SB` en el `symbol` (ej `A11LD.SB`).
- Mucho mas volumen de tickers porque SENEBI agrupa toda emision corporativa
  bilateral, no solo las listadas en panel principal.

---

## 10. Panel — Opciones

**Endpoint:** `POST /options`

Opciones de acciones argentinas. **~429 items**.

### Body

```json
{}
```

### Response

**list directa**.

### Schema

```json
{
  "tradeVolume": 1.0,
  "symbol": "ALUC1000AG",
  "imbalance": 0.0,
  "previousSettlementPrice": 0.0,
  "offerPrice": 0.0,
  "openInterest": 0.0,
  "vwap": 65.0,
  "description": "",
  "numberOfOrders": 1,
  "openingPrice": 65.0,
  "optionType": "CALL",
  "tickDirection": 0,
  "underlyingSymbol": "ALUA",
  "securityDesc": "",
  "securitySubType": "",
  "maturityDate": "2026-08-21",
  "previousClosingPrice": 0.0,
  "settlementType": "2",
  "quantityOffer": 0.0,
  "tradingHighPrice": 65.0,
  "denominationCcy": "ARS",
  "bidPrice": 0.0,
  "tradingLowPrice": 65.0,
  "market": "BYMA",
  "volumeAmount": 6500.0,
  "volume": 1.0,
  "trade": 65.0,
  "daysToMaturity": 78,
  "tradeHour": "14:59:50",
  "securityType": "OPT",
  "closingPrice": 65.0,
  "settlementPrice": 65.0,
  "quantityBid": 0.0
}
```

### Campos especificos

| Campo | Descripcion |
|-------|-------------|
| `optionType` | `CALL` o `PUT`. |
| `underlyingSymbol` | Activo subyacente (`ALUA`, `GGAL`, etc.). |
| `securityType` | `OPT`. |
| `maturityDate` | Vencimiento de la opcion. |
| `openInterest` | Interes abierto (real, no 0 como en acciones). |

### Decodificacion del ticker

Las opciones BYMA siguen el formato: `{ROOT}{C|V}{STRIKE}{MES}{AÑO?}`

`ALUC1000AG` → ALUA + C (Call) + 1000 (strike) + AG (Agosto)

> Para parsear consistentemente, usar el campo `strike` cuando este
> presente, o derivarlo de `underlyingSymbol` + posicion del strike.
> El esquema oficial requiere decodificar por contexto.

---

## 11. Historico — Instrumentos

**Endpoint:** `GET /chart/historical-series/history`

OHLCV historico de un instrumento (accion, CEDEAR, bono, ON, opcion).

### Query params

| Param | Descripcion |
|-------|-------------|
| `symbol` | **Formato: `{TICKER} 24HS`**. Ejemplo: `GGAL 24HS`. |
| `resolution` | `D` (diaria), `W` (semanal), `M` (mensual). |
| `from`, `to` | Unix timestamp en segundos UTC. |

### Formato simbolo

| Tipo de instrumento | Formato | Ejemplo |
|---------------------|---------|---------|
| Accion ARS | `TICKER 24HS` | `GGAL 24HS` |
| Accion USD MEP | `TICKERD 24HS` | (raro) |
| CEDEAR ARS | `TICKER 24HS` | `AAPL 24HS` |
| CEDEAR USD | `TICKERD 24HS` | `AAPLD 24HS` |
| Bono soberano ARS | `TICKER 24HS` | `AL30 24HS` |
| Bono soberano USD | `TICKERD 24HS` | `AL30D 24HS` |
| Bono soberano CCL | `TICKERC 24HS` | `AL30C 24HS` |
| LECAP/BONCAP | `TICKER 24HS` | `TY30P 24HS`, `TZX26 24HS` |
| Opcion | `OPTSYMBOL 24HS` | `ALUC1000AG 24HS` (suele estar vacio) |

> ⚠️ **Sufijo CI no funciona** en historicos — retorna HTTP 400.
> ⚠️ **48HS funciona pero retorna 0 puntos** (no se negocia ese settlement con regularidad).
> ⚠️ **Sin sufijo retorna 400** — siempre incluir `24HS`.

### Response

```json
{
  "s": "ok",
  "t": [1715569200, 1715655600, 1715742000, ...],
  "o": [3500.0, 3520.5, 3490.0, ...],
  "h": [3550.0, 3540.0, 3510.0, ...],
  "l": [3480.0, 3490.0, 3460.0, ...],
  "c": [3520.0, 3510.0, 3495.0, ...],
  "v": [50000, 65000, 42000, ...]
}
```

### Campos

| Campo | Descripcion |
|-------|-------------|
| `s` | Status: `"ok"`, `"no_data"`, `"error"`. |
| `t[]` | Timestamps unix UTC seconds (alineados por indice con OHLCV). |
| `o[]` | Open. |
| `h[]` | High. |
| `l[]` | Low. |
| `c[]` | Close. |
| `v[]` | Volume. |

### Comportamiento de resolution

| Resolution | Comportamiento |
|------------|----------------|
| `D` | Diario — funciona como esperado. |
| `W` | Semanal — agrega 5 dias en 1 bar. |
| `M` | Mensual — agrega ~22 dias en 1 bar. |
| `1`, `5`, `15`, `60`, `240` | La API acepta pero retorna el mismo set que `D` (intraday no expuesto). |

---

## 12. Historico — Indices

**Endpoint:** `GET /chart/index-historical-series/history`

Serie historica de un indice BYMA.

### Query params

Igual que historico de instrumentos:

| Param | Descripcion |
|-------|-------------|
| `symbol` | Codigo de letra del indice (ej: `M`, `G`). |
| `resolution` | `D` (la API ignora este parametro en indices). |
| `from`, `to` | Unix timestamp seconds UTC. |

### Indices verificados con datos

| Codigo | Indice | Rango tipico (Jun 2026) |
|--------|--------|-------------------------|
| `M` | **S&P MERVAL** | 2.3M - 3.2M |
| `G` | **BURCAP** | 100M - 137M |

### Indices que existen pero retornan ceros

`A`, `B`, `V` y otras letras retornan HTTP 200 con `c[]` lleno de 0.0
— probablemente indices deprecated o sin publicacion historica oficial.

### Response

Mismo schema que historico de instrumentos:

```json
{
  "s": "ok",
  "t": [1715569200, ...],
  "o": [...], "h": [...], "l": [...], "c": [...], "v": [...]
}
```

> ⚠️ El campo `v[]` (volumen) tipicamente es 0 en indices.

---

## 13. Bond Info — Ficha tecnica de bonos / ONs

**Endpoint:** `POST /bnown/fichatecnica/especies/general`

Ficha tecnica completa de un bono, LECAP, BONCAP u ON: ley aplicable,
forma de amortizacion, esquema de intereses (cupones), fechas de
emision/vencimiento, ISIN, moneda, monto nominal/residual, emisor.

Es el endpoint principal para **calculos de cashflow** porque devuelve el
texto oficial con el cronograma de amortizacion y la formula de
intereses (incluido step-up para bonos con tasas crecientes).

### Body

```json
{"symbol": "AE38"}
```

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `symbol` | string | Ticker SIN sufijo de settlement. Ej: `AE38`, `AL30`, `GD30`, `BPOA7`, `TY30P`, `S237Q`, `SBC1C`. Tambien acepta variantes por moneda: `AE38C`, `AE38D`. |

> ⚠️ Payload vacio (`{}`) retorna 200 con `data: []` y `empty: true`.
> Payload `null` retorna 400 ("Failed to read request").

### Response

```json
{
  "content": {
    "page_number": 1,
    "page_count": 1,
    "page_size": 50,
    "total_elements_count": 1
  },
  "data": [
    {
      "ley": "Nacional",
      "formaAmortizacion": "La amortizacion se efectuara en VEINTIDOS (22) cuotas semestrales iguales el 9 de enero y el 9 de julio de cada año, con la primera cuota el 9 de julio de 2027 y la ultima cuota el 9 de enero de 2038.\nLa totalidad de las condiciones definitivas de la presente emision constan en la Resolucion N° 381/2020 del Ministerio de Economia de la Nacion publicada el 18.08.2020 en el Boletin Oficial.",
      "denominacionMinima": 1,
      "fechaVencimiento": "2038-01-09 00:00:00.0",
      "tipoGarantia": "Comun",
      "fechaEmision": "2020-09-04 00:00:00.0",
      "fechaDevenganIntereses": "",
      "codigoIsin": "ARARGE3209U2",
      "tipoEspecie": "Titulos Publicos",
      "default": "",
      "tipoObligacion": "Valores Publicos Nacionales",
      "montoNominal": 10063292009,
      "denominacion": "BONOS DE LA REPUBLICA ARGENTINA EN DOLARES ESTADOUNIDENSES STEP UP 2038",
      "insType": "BOND",
      "paisLey": "",
      "moneda": "Dolares",
      "montoResidual": 10063292009,
      "interes": "Devengaran intereses, sobre la base de un año de 360 dias integrado por 12 meses de 30 dias cada uno, de acuerdo con las siguientes tasas anuales:\ni. Del 4 de septiembre de 2020 (inclusive) al 9 de julio de 2021 (exclusive): 0,125%.\nii. Del 9 de julio de 2021 (inclusive) al 9 de julio de 2022 (exclusive): 2,00%.\niii. Del 9 de julio de 2022 (inclusive) al 9 de julio de 2023 (exclusive): 3,875%.\niv. Del 9 de julio de 2023 (inclusive) al 9 de julio de 2024 (exclusive): 4,25%.\nv. Del 9 de julio de 2024 (inclusive) al vencimiento: 5,00%.",
      "emisor": "Gobierno Nacional"
    }
  ],
  "empty": false,
  "upgrade": false
}
```

### Campos de `data[0]`

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `ley` | string | Jurisdiccion aplicable: `Nacional`, `Extranjera`, `Nueva York`, `Inglaterra`. Critico para distinguir AL30 (ley local) de GD30 (ley NY). |
| `formaAmortizacion` | string | **TEXTO PLANO** con el cronograma de amortizacion. Tipicamente especifica numero de cuotas, periodicidad (semestral/trimestral), fechas exactas y monto/proporcion por cuota. Para bullet: `"Al vencimiento"`. |
| `denominacionMinima` | int | Denominacion minima de emision (ej: `1` = 1 unidad, `100` = laminas de $100). |
| `fechaVencimiento` | string | Fecha de vencimiento en formato `YYYY-MM-DD HH:MM:SS.f`. |
| `tipoGarantia` | string | Tipo de garantia: `Comun`, `Con Garantia Especifica`, etc. |
| `fechaEmision` | string | Fecha de emision del bono. |
| `fechaDevenganIntereses` | string | Fecha de inicio del devengo de intereses (suele estar vacia si coincide con emision). |
| `codigoIsin` | string | Codigo ISIN (International Securities Identification Number). |
| `tipoEspecie` | string | `Titulos Publicos`, `Obligaciones Negociables`, `Letras del Tesoro`. |
| `default` | string | Estado de default (vacio si esta al dia). |
| `tipoObligacion` | string | Clasificacion regulatoria: `Valores Publicos Nacionales`, `Provinciales`, `Corporativos`. |
| `montoNominal` | int | Monto nominal total emitido (en unidades de la moneda). |
| `denominacion` | string | Nombre oficial completo del bono. |
| `insType` | string | `BOND` (siempre). |
| `paisLey` | string | Pais de la ley aplicable (texto libre, puede estar vacio). |
| `moneda` | string | Moneda en texto: `Dolares`, `Pesos`, `Pesos Ajustables por CER`, `Dolar Linked`. |
| `montoResidual` | int | Monto residual actual (post-amortizaciones). |
| `interes` | string | **TEXTO PLANO** con esquema de devengo de intereses. Para step-up describe cada tramo de tasa. Para tasa fija da el valor. Para CER/Dolar-linked describe el indice ajuste. |
| `emisor` | string | Emisor: `Gobierno Nacional`, `Provincia de Buenos Aires`, `YPF S.A.`, etc. |

### Ejemplos de aplicacion

**1. Distinguir AL30 (ley local) vs GD30 (ley NY):**

```python
al30 = fetch_bond_info("AL30")
gd30 = fetch_bond_info("GD30")
print(al30['data'][0]['ley'])  # "Nacional"
print(gd30['data'][0]['ley'])  # "Nueva York" (mas seguro juridicamente)
```

**2. Parsear cronograma de amortizacion (AE38):**

```python
info = fetch_bond_info("AE38")
texto = info['data'][0]['formaAmortizacion']
# "22 cuotas semestrales iguales el 9 de enero y el 9 de julio,
#  primera 9 julio 2027, ultima 9 enero 2038"
# -> ~4.545% del nominal por cuota, 22 cuotas
```

**3. Detectar step-up vs tasa fija:**

```python
info = fetch_bond_info("AE38")
if "tasas anuales" in info['data'][0]['interes'].lower():
    print("Step-up bond")
```

### Variantes y limitaciones

| Caso | Comportamiento |
|------|----------------|
| Ticker valido (bono/ON/LECAP) | 200 con ficha completa |
| Variante por moneda (`AE38C`, `AE38D`) | 200 con misma ficha (datos de emisor) |
| Accion (`GGAL`, `AAPL`) | 200 con `data: []` (vacio) |
| Opcion / caucion | 200 con `data: []` (vacio) |
| Ticker inexistente | 200 con `data: []` |
| Payload vacio `{}` | 200 con `data: []` y `empty: true` |
| Payload `null` | 400 `"Failed to read request"` |

### Encoding

Los textos largos (`formaAmortizacion`, `interes`) pueden contener
caracteres latin-1 que se muestran como `?` en consolas Windows pero se
salvan correctamente con `json.dumps(..., ensure_ascii=False)` a archivos UTF-8.

---

## 14. Codigos: settlementType, securityType, securitySubType, market

### `settlementType`

| Valor | Significado |
|-------|-------------|
| `"1"` | CI (Contado Inmediato — T+0) |
| `"2"` | 24hs (T+1) |
| `"3"` | 48hs (T+2) — practicamente no se usa hoy |

### `securityType`

| Codigo | Tipo | Aparece en |
|--------|------|------------|
| `CS` | Common Stock | leading-equity |
| `CD` | CEDEAR | cedears |
| `GO` | Government Obligation (bono soberano) | public-bonds |
| `CORP` | Corporate (ON) | negociable-obligations, senebi-obligaciones-negociables |
| `QS` | Caucion / Repo | cauciones |
| `OPT` | Option | options |

### `securitySubType`

| Codigo | Significado | Aparece en |
|--------|-------------|------------|
| `M` | Merval (panel general) | leading-equity |
| `B` | Bond | public-bonds |
| `""` | (vacio) | cedears, on, options, cauciones, senebi |

### `market`

| Codigo | Significado |
|--------|-------------|
| `BYMA` | Mercado principal BYMA |
| `SENEBI` | Sistema Electronico de Negociacion Bilateral |

### `denominationCcy`

| Codigo | Moneda |
|--------|--------|
| `ARS` | Pesos argentinos |
| `USD` | Dolar estadounidense (MEP) |
| `EXT` | EXTerior / CCL (Contado con Liquidacion) |

### `tickDirection`

| Valor | Significado |
|-------|-------------|
| `-1` | Down-tick (precio bajo vs trade anterior) |
| `0` | Sin cambio (o sin actividad) |
| `+1` | Up-tick (precio subio vs trade anterior) |

---

## 15. Paginacion: limitaciones y workaround

### Problema

Los endpoints POST devuelven en el `content` un campo `page_count` que
sugiere paginacion (ej: `page_count: 6` para public-bonds). Sin embargo,
**el parametro `page` en el body es IGNORADO** por la API actual.

Evidencia experimental:

```python
# Todas estas variantes retornan SIEMPRE pagina 1:
post("public-bonds", {"page": 2, "page_size": 10})
post("public-bonds", {"page_number": 2, "page_size": 10})
post("public-bonds", {"pageNumber": 2, "pageSize": 10})
post("public-bonds", {"current_page": 2})
post("public-bonds", {"offset": 10, "limit": 10})
# El response siempre tiene content.page_number == 1, data[0].symbol == "AE38"
```

Tampoco funciona:
- `Content-Type: application/x-www-form-urlencoded` (415 Unsupported)
- Headers extra (`Origin`, `Referer`, `X-Requested-With`)
- camelCase de los params

### Workaround

Usar `page_size` grande para traer todo el dataset en una sola llamada:

```python
post("public-bonds", {"page_size": 2000})       # 1018 items en 1 call
post("senebi-obligaciones-negociables", {"page_size": 5000})  # 3160 items
```

El script `fetch_byma.py` expone esto via flag `--all` que setea
`page_size=5000` automaticamente.

### Tabla por panel

| Panel | Total items observado | Pagination util? |
|-------|----------------------|------------------|
| `leading-equity` | 40 | No (cabe en defaults) |
| `cedears` | 2000 | No (devuelve list directa, sin pagination) |
| `public-bonds` | 1018 | Page IGNORADO. Usar page_size=2000 |
| `negociable-obligations` | 2117 | No (devuelve list directa) |
| `cauciones` | 133 | No |
| `senebi-obligaciones-negociables` | 3160 | Page IGNORADO. Usar page_size=5000 |
| `options` | 429 | No |

---

## 16. Manejo de errores

| Status | Causas tipicas |
|--------|----------------|
| 200 | OK — verificar response.s == "ok" en historicos. |
| 400 | Simbolo invalido en historico, sin sufijo `24HS`, o param requerido faltante. |
| 401 | Endpoint inexistente (BYMA usa 401 generico, no 404). |
| 415 | Content-Type erroneo (POST debe ser `application/json`). |
| 500 | Error interno de BYMA. |

### Patrones de error en historicos

- `symbol=GGAL` (sin sufijo) → **400** (body vacio).
- `symbol=GGAL CI` (sufijo CI no soportado) → **400**.
- `symbol=GGAL 48HS` → **200 con t=[]**.
- `symbol=AAPL 24HS` (CEDEAR valido) → **200 con datos**.

### Paths que retornan 401

Cualquier path no incluido en la lista oficial:
- `/indices`, `/indexes`, `/symbols`, `/search`, `/leading-bonds`, etc.

---

## 17. Consideraciones tecnicas

### Rate limiting

No documentado ni observado limite. Se recomienda:

- Minimo **0.3 segundos** entre requests.
- El `all` mode usa `time.sleep(0.3)` entre cada llamada.
- Para batches > 50 requests, considerar pool con `aiohttp` con
  concurrency cap = 5.

### Delay de los datos

- **Paneles intradia**: tiempo real (15-min delay tipico de mercado argentino).
- **Historicos**: T-1 disponible al cierre del dia siguiente (~19hs ART).

### Horarios de mercado

- **Rueda BYMA**: 11:00 - 17:00 ART (Lunes a Viernes).
- **Pre-mercado / Post-mercado**: limitado, mayormente no operativo.

### Encoding

API retorna UTF-8 valido. No hay problemas de encoding como en MAE.

### CORS

API admite CORS para `localhost` y dominios oficiales de BYMA.
Para uso desde frontend, considerar proxy de cache.

### Disponibilidad

- API disponible 24/7.
- Datos se actualizan solo en horario de rueda.
- Fines de semana y feriados: snapshots devuelven datos del ultimo dia habil.

### Aviso legal

- API publica de BYMA, sin documentacion oficial.
- Los endpoints **pueden cambiar sin aviso**.
- Para uso comercial intensivo, contactar BYMA para licencias oficiales.

---

## Referencias

- **BYMA Oficial:** https://www.byma.com.ar
- **Open Market Data:** https://open.bymadata.com.ar
- **CNV (regulador):** https://www.cnv.gov.ar
- **Listado oficial de simbolos:** ver paneles via API
