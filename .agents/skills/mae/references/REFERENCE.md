# MAE — Referencia Completa de la API

> **MAE** = Mercado Abierto Electronico de Argentina. Mercado mayorista de
> renta fija, cauciones, REPO, FOREX, contratos de futuro de dolar (DDF) e
> indice ARS-MAE. Esta documentacion cubre la API publica de market data
> expuesta en `api.marketdata.mae.com.ar`.

---

## Indice

1. [Resumen de endpoints](#1-resumen-de-endpoints)
2. [Convenciones de la API](#2-convenciones-de-la-api)
3. [Resumen — top 10 intradia por categoria](#3-resumen--top-10-intradia-por-categoria)
4. [Datos — cotizaciones completas del dia](#4-datos--cotizaciones-completas-del-dia)
5. [Volumen — volumen por categoria de mercado](#5-volumen--volumen-por-categoria-de-mercado)
6. [Mapa — prospectos por segmento/plazo/moneda](#6-mapa--prospectos-por-segmentoplazomoneda)
7. [Comunicados institucionales](#7-comunicados-institucionales)
8. [Licitaciones — calendario](#8-licitaciones--calendario)
9. [Licitaciones por estado — detalle filtrado](#9-licitaciones-por-estado--detalle-filtrado)
10. [Flujo de fondos cotizaciones — curvas RF](#10-flujo-de-fondos-cotizaciones--curvas-rf)
11. [Historico renta fija](#11-historico-renta-fija)
12. [Historico FOREX](#12-historico-forex)
13. [Historico FOREX — volumen operado](#13-historico-forex--volumen-operado)
14. [Historico cauciones](#14-historico-cauciones)
15. [Cauciones — series de volumen y tasas](#15-cauciones--series-de-volumen-y-tasas)
16. [Historico REPO](#16-historico-repo)
17. [REPO — volumen y tasa por fecha](#17-repo--volumen-y-tasa-por-fecha)
18. [Indice ARS-MAE — snapshot intradia](#18-indice-ars-mae--snapshot-intradia)
19. [Indice ARS-MAE — historico diario](#19-indice-ars-mae--historico-diario)
20. [Codigos: segmentos, plazos, monedas, ruedas](#20-codigos-segmentos-plazos-monedas-ruedas)
21. [Manejo de errores](#21-manejo-de-errores)
22. [Consideraciones tecnicas](#22-consideraciones-tecnicas)

---

## 1. Resumen de endpoints

| # | Modo CLI | Endpoint | Metodo | Output |
|---|----------|----------|--------|--------|
| 1 | `resumen <tipo>` | `/api/mercado/resumen/{RF\|CAU\|FOR\|DDF}` | GET | list ~5-10 items |
| 2 | `datos <tipo>` | `/api/mercado/datos/{RF\|CAU\|FOR}` | GET | list 3-289 items |
| 3 | `volumen <moneda>` | `/api/mercado/volumen-categoria/{ARS\|USD}` | GET | list 6 items |
| 4 | `mapa` | `/api/mercado/mapa?oTitulo={...}` | GET | dict (claves $/D/C) |
| 5 | `comunicados` | `/api/institucional/comunicados[?oTitulo={...}]` | GET | list 60 items |
| 6 | `licitaciones` | `/api/mercado/licitaciones` | GET | dict {timeZone, events[]} |
| 7 | `licitaciones-estado` | `/api/mercado/licitacionesporestado/Todos?oTitulo={...}` | GET | list por estado |
| 8 | `flujo-fondos <letra>` | `/api/emisiones/flujofondoscotiz/{B\|H}` | GET | list cashflows |
| 9 | `hist-rf` | `/api/mercado/titulo/historicorentafija?oTitulo={...}` | GET | dict {grid, chart} |
| 10 | `hist-forex` | `/api/mercado/titulo/historicoforex?oTitulo={...}` | GET | list por dia |
| 11 | `hist-forex-vol` | `/api/mercado/titulo/historicoforex/volumenoperado?oTitulo={...}` | GET | list por dia |
| 12 | `hist-cau` | `/api/mercado/titulo/historicocauciones?oTitulo={...}` | GET | list por dia |
| 13 | `hist-cau-vt` | `/api/mercado/cauciones/valorescierre/volumentasas?oTitulo={...}` | GET | dict {tasa[], volumen[]} |
| 14 | `hist-repo` | `/api/mercado/titulo/historicorepo?oTitulo={...}` | GET | list por dia con detalle por rueda |
| 15 | `repo-fecha` | `/api/mercado/repo/titulosfecha?oTitulo={...}` | GET | list por fecha (volumen + tasaPP) |
| 16 | `indice-ars` | `/api/mercado/indiceARS` | GET | list 10 puntos intradia |
| 17 | `indice-ars-hist` | `/api/mercado/titulo/indicearsmae/historico?oTitulo={...}` | GET | list por dia |

**Total: 17 endpoints publicos verificados ✅** (mas el endpoint `repo/tasas` que es alias 1:1 de `licitaciones`).

---

## 2. Convenciones de la API

### Base URL

```
https://api.marketdata.mae.com.ar/api
```

### Headers

La API tolera requests sin headers, pero conviene enviar:

```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}
```

### Parametro `oTitulo`

Todos los endpoints con filtros aceptan un parametro de query llamado
`oTitulo` cuyo valor es un **JSON URL-encoded**. Ejemplo:

```python
import json, urllib.parse
filtro = {"fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05"}
oTitulo = urllib.parse.quote(json.dumps(filtro))
url = f"/api/mercado/titulo/historicorentafija?oTitulo={oTitulo}"
```

Las keys que puede contener `oTitulo` varian por endpoint (ver tabla en
cada seccion). Las mas comunes:

- `fechaDesde`, `fechaHasta`: rango temporal (formato `YYYY-MM-DD`).
- `segmento`: codigo de segmento (BT, PPT, etc.).
- `plazo`: codigo de plazo (000, 001, 007, etc.).
- `moneda`: simbolo de moneda ($, D, C).
- `estado`: estado de licitacion (A, F, C, S, P).
- `codTitulo`: ticker (CAARS, CAUSD).
- `unit`: unidad de visualizacion (USD, ARS) — *frecuentemente ignorada*.

### Formato de fechas

- En `oTitulo`: `YYYY-MM-DD` (string).
- En responses: `ISO 8601` con offset (`2026-06-04T13:00:00Z`) o sin
  (`2026-06-04T00:00:00`). Algunos timestamps unix (segundos UTC) en
  series temporales (`time` field).

### Encoding

Algunos campos texto (titulo de licitaciones, comentarios) vienen con
caracteres en latin-1 que se muestran mal en consolas UTF-8. La API
declara `Content-Type: application/json; charset=utf-8` pero los strings
incluyen `í` (i acentuada) escapados como `?` cuando se imprime en
consola Windows. **Workaround**: leer con `resp.json()` y reescribir con
`json.dumps(..., ensure_ascii=False)` en archivos UTF-8.

---

## 3. Resumen — top 10 intradia por categoria

**Endpoint:** `GET /api/mercado/resumen/{tipo}`

Devuelve el **top 10 titulos lideres** de la categoria con su precio actual,
variacion, cantidad/monto del dia y un mini-grafico intradia (`datosGrafico`)
con las series de precios y volumenes ejecutados durante la rueda.

### Tipos validos

| Tipo | Descripcion | Items tipicos |
|------|-------------|---------------|
| `RF` | Renta Fija (LECAPs, BONCAPs, BOPREALes, ONs lideres) | ~10 |
| `CAU` | Cauciones (CAARS/CAUSD por plazo) | ~7 |
| `FOR` | FOREX (US$ Tran, EUR Tran, etc.) | ~5 |
| `DDF` | Dolar Diferido a Fix (futuros de dolar mensuales) | ~11 |

Cualquier otro valor (`REPO`, `DLR`, `RVA`, `ARS`, `ALL`, etc.) retorna **HTTP 400**.

### Ejemplo de request

```bash
GET /api/mercado/resumen/RF
```

### Schema del response (cada item)

```json
{
  "ticker": "S12J6",
  "tipoEmision": "TPN",
  "descripcion": "S12J6  (LECAP $ 2,10% 12/06)",
  "plazo": "001",
  "fechaLiquidacion": null,
  "moneda": "$",
  "segmento": "BT",
  "variacion": 0.07,
  "ultimo": 1.0258,
  "cantidad": 192530196652,
  "monto": 197448865291,
  "codigoOrden": null,
  "tickerOrden": null,
  "datosGrafico": {
    "ultimoHoy": 0,
    "variacionPerc": 0,
    "precios": [
      {"time": 1780574067, "value": 1.0255505},
      {"time": 1780580951, "value": 1.0253}
    ],
    "volumenes": [
      {"time": 1780574067, "value": 43902440000.0}
    ]
  },
  "tipoNegociacion": null
}
```

### Campos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `ticker` | string | Codigo del titulo (ej: `S12J6`, `CAARS`, `UST$T`, `DLR062026`). |
| `tipoEmision` | string | Tipo: `TPN` (Titulo Publico Nacional), `CAU` (Caucion), `FOR` (Forex), `DDF` (Dolar Diferido), `ON` (Obligacion Negociable). |
| `descripcion` | string | Descripcion humana del titulo entre parentesis. |
| `plazo` | string | Codigo de plazo (`000`=CI, `001`=24hs, `002`=48hs, `007`=7 dias). |
| `fechaLiquidacion` | string\|null | Fecha de liquidacion ISO8601 (o `null` si CI). |
| `moneda` | string | `$` (pesos), `D` (dolar MEP/CCL), `T` (dolar transferencia mayorista), `C` (dolar cable). |
| `segmento` | string | Codigo de segmento (`BT`=Bilateral TRD, `K`=Cauciones, `M`=Mayorista FOREX, `DDF`=Dolar Diferido). |
| `variacion` | float | Variacion porcentual vs cierre anterior. |
| `ultimo` | float | Ultimo precio operado (paridad si renta fija, tasa si caucion en %). |
| `cantidad` | float | Cantidad nominal/contratos negociados. |
| `monto` | float | Monto efectivo en moneda de cotizacion. |
| `datosGrafico.precios[]` | list | Serie intradia: `{time: unix_ts_seconds, value: float}`. |
| `datosGrafico.volumenes[]` | list | Serie intradia de volumenes: `{time: unix_ts_seconds, value: float}`. |
| `datosGrafico.ultimoHoy` | float | Ultimo precio del dia (suele venir 0 en items observados). |
| `datosGrafico.variacionPerc` | float | Variacion porcentual recalculada (suele venir 0). |
| `codigoOrden`, `tickerOrden`, `tipoNegociacion` | string\|null | Reservados (siempre null en observaciones). |

---

## 4. Datos — cotizaciones completas del dia

**Endpoint:** `GET /api/mercado/datos/{tipo}`

Devuelve **TODAS las cotizaciones** del dia para una categoria (no solo el
top 10 como `resumen`). Para `RF` puede devolver ~289 lineas (cada
combinacion `ticker × plazo × moneda`).

### Tipos validos

| Tipo | Descripcion | Items observados |
|------|-------------|------------------|
| `RF` | Renta Fija (todos los bonos, letras, ONs) | ~289 |
| `CAU` | Cauciones (CAARS, CAUSD por plazo) | ~3 |
| `FOR` | FOREX (todas las paridades) | ~14 |

**Tipos NO soportados** (retornan error):
- `DDF` → HTTP 500
- `REPO`, `DLR`, `all`, `BT`, `PPT`, `FCI`, etc. → HTTP 400

> Para FOR la lista tiene mas variedad que el `resumen` (incluye CNH yuan,
> EURO billete/transferencia, GBP, etc.).

### Schema del response (cada item)

```json
{
  "ticker": "AE38",
  "tipoEmision": "TPN",
  "fechaLiquidacion": "0001-01-01T00:00:00",
  "volumen": 6000000,
  "monto": 7151190360,
  "descripcion": "AE38  (BONO USD STEP UP 2038 L.A.)",
  "plazo": "000",
  "codigoPlazo": "000",
  "segmento": "Bilateral TRD",
  "codigoSegmento": "BT",
  "moneda": "$",
  "variacion": 0.75,
  "ultimo": 1196.0,
  "ultimaTasa": 0,
  "cierreAnterior": 0,
  "minimo": 1187.7301,
  "maximo": 1196.0,
  "openInterest": 0,
  "precioCierre": 1196.0,
  "precioApertura": null
}
```

### Campos extra vs `resumen`

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `volumen` | float | Cantidad nominal negociada. |
| `monto` | float | Monto efectivo (a veces aparecen invertidos: `volumen` puede ser el monto en pesos y viceversa segun categoria — verificar en cada item). |
| `codigoPlazo` | string | Codigo de plazo (suele coincidir con `plazo`). |
| `segmento` | string | Descripcion en texto (`Bilateral TRD`, `Mayorista`, `Minorista`). |
| `codigoSegmento` | string | Codigo del segmento (`BT`, `M`, `N`, `K`). |
| `ultimaTasa` | float | Ultima tasa operada (solo para cauciones y REPO; 0 en bonos). |
| `cierreAnterior` | float | Precio o tasa del cierre anterior. |
| `minimo`, `maximo` | float | Rango del dia. |
| `openInterest` | float | Interes abierto (solo DDF/REPO). |
| `precioCierre` | float\|null | Precio de cierre del dia. |
| `precioApertura` | float\|null | Precio de apertura. |

> `fechaLiquidacion: "0001-01-01T00:00:00"` es un sentinel para CI (contado
> inmediato) o sin liquidacion definida.

---

## 5. Volumen — volumen por categoria de mercado

**Endpoint:** `GET /api/mercado/volumen-categoria/{moneda}`

Devuelve el volumen del dia agrupado en `grupos` con su `share`
porcentual dentro del grupo.

### Monedas validas

| Moneda | Descripcion |
|--------|-------------|
| `ARS` | Pesos argentinos |
| `USD` | Dolares (conversion automatica) |

### Ejemplo de response

```json
[
  {"nombre": "Renta Fija TRD", "descripcion": "Renta Fija Trading", "volumen": 3747805856505, "share": 95.84, "grupo": "Contado", "moneda": "ARS", "orden": 1},
  {"nombre": "Renta Fija PPT", "descripcion": "Renta Fija PPT", "volumen": 162481251969, "share": 4.16, "grupo": "Contado", "moneda": "ARS", "orden": 2},
  {"nombre": "FOREX", "descripcion": "FOREX", "volumen": 856737345780, "share": 33.4, "grupo": "Monedas", "moneda": "ARS", "orden": 1}
]
```

### Campos

| Campo | Descripcion |
|-------|-------------|
| `nombre` | Nombre corto de la categoria. |
| `descripcion` | Descripcion larga. |
| `volumen` | Volumen del dia en la moneda solicitada. |
| `share` | Share porcentual dentro del grupo (no del total). |
| `grupo` | `Contado` (renta fija contado), `Monedas` (FOREX), etc. |
| `moneda` | `ARS` o `USD` (el mismo que se pidio). |
| `orden` | Orden de display sugerido. |

---

## 6. Mapa — prospectos por segmento/plazo/moneda

**Endpoint:** `GET /api/mercado/mapa?oTitulo={...}`

Devuelve la **lista de titulos negociados** en el segmento/plazo
especificado, agrupada por moneda y subdividida en publicos vs privados.

### Parametros `oTitulo`

```json
{"segmento": "BT", "plazo": "001", "moneda": "$"}
```

| Key | Tipo | Valores aceptados |
|-----|------|-------------------|
| `segmento` | string | `BT`, `PPT`, `PT`, `BL`, `TX`, `RV`, `EX` (mas — ver tabla seccion 20). |
| `plazo` | string | `000` (CI), `001` (24hs), `002` (48hs), `007` (7d). |
| `moneda` | string | `$`, `D`, `C`. |

> **Importante**: el response SIEMPRE devuelve las 3 monedas (`$`, `D`, `C`)
> aunque se solicite una sola. El filtro por moneda parece ser solo
> informativo para el frontend.

### Schema del response

```json
{
  "$": {
    "Privados": [ { ...cotizacion... }, ... ],
    "Publicos": [ { ...cotizacion... }, ... ]
  },
  "D": { "Privados": [], "Publicos": [] },
  "C": { "Privados": [], "Publicos": [] }
}
```

Cada cotizacion tiene el mismo schema que `/datos/RF` (ver seccion 4),
pero `datosGrafico` siempre es `null`.

---

## 7. Comunicados institucionales

**Endpoint:** `GET /api/institucional/comunicados[?oTitulo={...}]`

Devuelve los comunicados publicados por el MAE: altas de membresia,
ampliaciones de emisiones, autorizaciones, etc.

### Parametros opcionales (`oTitulo`)

```json
{"fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05"}
```

Sin filtro: devuelve los **ultimos 60 comunicados** (ordenados por fecha desc).

### Schema del response (cada item)

```json
{
  "id": 15639,
  "fecha": "2026-06-04T03:00:00Z",
  "numero": 14456,
  "titulo": "Alta AG VALORES S.A - Membresia Plena",
  "tipo": "MAE",
  "archivos": [
    {
      "nombre": "Alta AG VALORES S.A - Membresia Plena",
      "url": "https://mercadoabierto.sharepoint.com/:b:/s/mae-archivos-publicos/IQA..."
    }
  ]
}
```

### Campos

| Campo | Descripcion |
|-------|-------------|
| `id` | ID interno autoincremental. |
| `fecha` | Fecha de publicacion (UTC, hora 03:00:00 es UTC = 00:00 ART). |
| `numero` | Numero de comunicado oficial. |
| `titulo` | Titulo del comunicado. |
| `tipo` | `MAE` (en todas las observaciones). |
| `archivos` | Lista de PDFs adjuntos (SharePoint URLs publicas). |

> Los PDFs estan en SharePoint publico — **no requieren autenticacion**.

---

## 8. Licitaciones — calendario

**Endpoint:** `GET /api/mercado/licitaciones`

Calendario simple de licitaciones primarias en curso o proximas.
**Alias:** `GET /api/mercado/repo/tasas` (devuelve el mismo response).

### Schema del response

```json
{
  "timeZone": "UTC",
  "events": [
    {
      "id": -621,
      "title": "TITULOS DE DEUDA BANCO DE LA PROVINCIA DE BUENOS AIRES CLASE V",
      "start": "2026-06-04T13:00:00Z",
      "end": "2026-06-04T19:00:00Z"
    }
  ]
}
```

| Campo | Descripcion |
|-------|-------------|
| `id` | ID de la licitacion (negativo). Coincide con el `id` de `licitaciones-estado`. |
| `title` | Titulo de la licitacion. |
| `start`, `end` | Apertura y cierre en UTC ISO8601. |

> **Para detalle completo** (emisor, monto, modalidad, colocadores) usar
> `licitaciones-estado` (seccion 9).

---

## 9. Licitaciones por estado — detalle filtrado

**Endpoint:** `GET /api/mercado/licitacionesporestado/Todos?oTitulo={...}`

Devuelve las licitaciones con **todo el detalle** filtradas por estado y
rango de fechas. Es la fuente mas completa para conocer condiciones de
emision, colocadores, resultados de adjudicacion, etc.

### Parametros `oTitulo` (requeridos)

```json
{"estado": "A", "fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05"}
```

### Estados validos

| Codigo | Estado | Observaciones |
|--------|--------|---------------|
| `A` | Activa | Licitaciones en curso o programadas |
| `F` | Finalizada | Ya adjudicadas |
| `C` | Cancelada | Licitaciones canceladas (raro) |
| `S` | Suspendida | Suspendidas (suele venir vacio) |
| `P` | Programada | Programadas a futuro |

**Estados invalidos** (retornan HTTP 400):
- `M`, `X`, `N`, `I`, `T`, `Todos`, `TODOS`.

### Schema del response (cada item)

```json
{
  "fechaInicio": "2026-06-04T13:00:00Z",
  "fechaFin": "2026-06-04T19:00:00Z",
  "fechaLiquidacion": "2026-06-08T03:00:00Z",
  "fechaVencimiento": "2027-06-08T03:00:00Z",
  "fechaVencimientoEspecie": "2027-06-08T03:00:00Z",
  "titulo": "TITULOS DE DEUDA BANCO DE LA PROVINCIA DE BUENOS AIRES CLASE V",
  "emisor": "BANCO DE LA PROVINCIA DE BUENOS AIRES",
  "industria": "",
  "moneda": "USD",
  "ampliableHasta": "EL MONTO DISPONIBLE DEL PROGRAMA EN CONJUNTO CON LA CLASE VI",
  "variableLicitar": "TASA",
  "montoaLicitar": 20000000,
  "rueda": "BPBA",
  "modalidad": "Abierta",
  "liquidador": "Clear",
  "estado": "Activa",
  "tipo": "Publica",
  "colocador": "BANCO DE LA PROVINCIA DE BUENOS AIRES, BANCO DE GALICIA Y BUENOS AIRES S.A. ...",
  "observaciones": "Los Titulos de Deuda Clase V seran Suscriptos, Integrados y Pagaderos en Dolares Estadounidenses ...",
  "monto_Adjudicado": 31757262,
  "sistema_Adjudicacion": "Holandes",
  "valor_Corte": "TASA DE CORTE: 4.25%",
  "duration": "0.99 AÑOS",
  "id": -621,
  "existeArchivo": 0,
  "comentario": "...",
  "fechaModificacion": "...",
  "monedaMonto": "...",
  "plazoEspecie": "...",
  "archivos": []
}
```

### Campos principales

| Campo | Descripcion |
|-------|-------------|
| `titulo`, `emisor`, `industria` | Identificacion del emisor. |
| `moneda` | Moneda de emision (`USD`, `ARS`, `EUR`). |
| `montoaLicitar` | Monto base ofrecido. |
| `ampliableHasta` | Condicion textual de ampliacion. |
| `variableLicitar` | Variable de licitacion: `TASA`, `PRECIO`, `MONTO`. |
| `rueda` | Codigo de rueda (`BPBA`, `BNAC`, etc.). |
| `modalidad` | `Abierta`, `Cerrada`. |
| `liquidador` | `Clear`, `CRYL`, etc. |
| `estado` | Estado en texto (`Activa`, `Finalizada`, etc.). |
| `tipo` | `Publica`, `Privada`. |
| `colocador` | Lista de colocadores separados por espacios. |
| `monto_Adjudicado` | Monto efectivamente adjudicado. |
| `sistema_Adjudicacion` | `Holandes` (uniforme), `Americano` (multiple precio). |
| `valor_Corte` | Tasa o precio de corte (campo texto). |
| `duration` | Duration del instrumento. |
| `id` | ID negativo (mismo que `licitaciones` calendario). |
| `archivos` | PDFs adjuntos (cuando `existeArchivo == 1`). |

---

## 10. Flujo de fondos cotizaciones — curvas RF

**Endpoint:** `GET /api/emisiones/flujofondoscotiz/{letra}`

Devuelve el **flujo de fondos teorico** + precio de mercado + TIR + MD de
los bonos cotizantes de la letra solicitada. Sirve para construir curvas
de tasa o duration vs TIR.

### Letras con datos

| Letra | Categoria | Items observados |
|-------|-----------|------------------|
| `B` | BOPREALes Serie 1 (BPOB7, BPOD7, BPOC7) | 3 |
| `H` | Bonos hard dollar step-up (AE38, AL30, GD30, ...) | 6 |

**Letras sin datos** (response: `[]`): A, D-G, I-V (todas excepto B y H).
**Letra que falla** (HTTP 500): `C`.

### Schema del response (cada item)

```json
{
  "especie": "AE38",
  "numeroCuponActual": null,
  "renta": 0.0,
  "amortizacion": 0.0,
  "amasR": 0.0,
  "moneda": "D  ",
  "descripcion": "BONO USD STEP UP 2038 L.A.",
  "precio": 0.8195,
  "tir": 9.772563485731329,
  "md": 4.565667004694558,
  "detalle": [
    {
      "fechaPago": "2026-07-09T00:00:00",
      "numeroCupon": null,
      "vr": 100.0,
      "vrCartera": 100.0,
      "cashFlow": 2.5,
      "renta": 2.5,
      "amortizacion": 0.0,
      "amasR": 2.5
    }
  ]
}
```

### Campos

| Campo | Descripcion |
|-------|-------------|
| `especie` | Ticker del bono. |
| `descripcion` | Descripcion humana. |
| `moneda` | `D  ` (dolar — 3 caracteres por padding) o `$`. |
| `precio` | Precio actual de cotizacion. |
| `tir` | Tasa interna de retorno (anual %). |
| `md` | Modified Duration (años). |
| `renta`, `amortizacion`, `amasR` | Componentes del proximo cupon (suelen venir en 0 si esta cerca del corte). |
| `numeroCuponActual` | Numero de cupon corriente (puede ser null). |
| `detalle[]` | Lista completa de cashflows futuros: `fechaPago`, `vr` (valor residual), `vrCartera`, `cashFlow` (total), `renta`, `amortizacion`, `amasR` (amortizacion + renta). |

---

## 11. Historico renta fija

**Endpoint:** `GET /api/mercado/titulo/historicorentafija?oTitulo={...}`

Historico de operaciones de renta fija agrupado por dia.

### Parametros `oTitulo` (requeridos)

```json
{"fechaDesde": "2026-05-05", "fechaHasta": "2026-06-04"}
```

### Schema del response

```json
{
  "grid": [
    {
      "fecha": "2026-06-04T00:00:00",
      "volumen": 3889592416944.47,
      "details": [
        { ...cotizacion individual... },
        ...
      ]
    }
  ],
  "chart": [ ... ]
}
```

Cada `details[]` contiene el mismo schema que `/datos/RF` (seccion 4).
El `chart[]` es la serie temporal de volumen total para grafico.

---

## 12. Historico FOREX

**Endpoint:** `GET /api/mercado/titulo/historicoforex?oTitulo={...}`

Historico FOREX agrupado por dia con detalle por moneda/plazo/segmento.

### Parametros `oTitulo`

```json
{"fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05"}
```

### Schema

```json
[
  {
    "fecha": "2026-06-04T00:00:00",
    "cantidad": 3426955783120,
    "volumen": 2392952776,
    "details": [
      {
        "fecha": "2026-06-04T00:00:00",
        "ticker": "CNH$T",
        "descripcion": "CNH$T  (CHINESE YUAN TRAN A PESOS TRAN)",
        "moneda": "T",
        "plazo": "001",
        "codigoPlazo": "001",
        "segmento": "Mayorista",
        "codigoSegmento": "M",
        "volumen": 2000000,
        "monto": 425400000,
        "minimo": 212.7,
        "maximo": 212.7,
        "ultimo": 212.7,
        "variacion": 0.0,
        "tipoEmision": "FOR",
        "precioCierre": 212.7,
        "cant_Millones": 0,
        "fechaLiquidacion": "0001-01-01T00:00:00",
        "ultimaTasa": 0,
        "cierreAnterior": 0,
        "openInterest": 0,
        "precioApertura": null
      }
    ]
  }
]
```

> `cantidad` (top-level) es el total de unidades de moneda negociadas.
> `volumen` es el equivalente en dolares (o pesos).

---

## 13. Historico FOREX — volumen operado

**Endpoint:** `GET /api/mercado/titulo/historicoforex/volumenoperado?oTitulo={...}`

Serie simplificada de volumen total FOREX por dia, sin detalle por moneda.

### Schema

```json
[
  {"fecha": "2026-05-05T00:00:00", "volumen": 735007.5505, "cant_Millones": 526.701}
]
```

| Campo | Descripcion |
|-------|-------------|
| `fecha` | Fecha de la rueda (ISO8601). |
| `volumen` | Volumen total operado (en miles de dolares — ver `cant_Millones`). |
| `cant_Millones` | Cantidad de millones de moneda negociada. |

---

## 14. Historico cauciones

**Endpoint:** `GET /api/mercado/titulo/historicocauciones?oTitulo={...}`

Historico de cauciones agrupado por dia con detalle por titulo/plazo.

### Schema

```json
[
  {
    "fecha": "2026-06-04",
    "volumen": 3412662150818.0,
    "details": [
      {
        "fecha": "2026-06-04T00:00:00",
        "montoConcertado": 234659112.0,
        "montoColocador": 0,
        "montoTomador": 0,
        "tasaColocador": 0,
        "tasaTomador": 0,
        "tasaPP": 1.8356,
        "ticker": "CAUSD",
        "tipoEmision": "CAU",
        "fechaLiquidacion": "2026-06-05T00:00:00",
        "volumen": 0,
        "monto": 0,
        "descripcion": "CAUSD D 001",
        "plazo": "001",
        "moneda": "D",
        "variacion": 0.0,
        "ultimo": 0,
        "ultimaTasa": 1.6,
        "cierreAnterior": 1.6,
        "minimo": 1.3,
        "maximo": 2.49,
        "openInterest": 0,
        "precioCierre": null,
        "precioApertura": null
      }
    ]
  }
]
```

### Campos especificos de cauciones

| Campo | Descripcion |
|-------|-------------|
| `montoConcertado` | Monto total operado (suma de colocador + tomador). |
| `montoColocador`, `montoTomador` | Montos por punta (frecuentemente vienen en 0). |
| `tasaColocador`, `tasaTomador` | Tasas por punta. |
| `tasaPP` | Tasa promedio ponderada del dia. |
| `ultimaTasa` | Ultima tasa operada (en % anual). |
| `cierreAnterior` | Tasa de cierre del dia anterior. |
| `minimo`, `maximo` | Tasas minima y maxima del dia. |

---

## 15. Cauciones — series de volumen y tasas

**Endpoint:** `GET /api/mercado/cauciones/valorescierre/volumentasas?oTitulo={...}`

Series temporales separadas de tasa y volumen para una caucion especifica
(titulo + plazo). Ideal para graficos.

### Parametros `oTitulo`

```json
{"codTitulo": "CAARS", "plazo": "001", "fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05"}
```

### Tickers validos

| Ticker | Descripcion |
|--------|-------------|
| `CAARS` | Caucion en pesos |
| `CAUSD` | Caucion en dolares |
| `CAU` | Aggregated (parece devolver todo CAARS+CAUSD) |

### Plazos comunes

| Plazo | Dias |
|-------|------|
| `001` | 1 dia |
| `007` | 7 dias |

### Schema

```json
{
  "tasa": [
    {"time": 1779840000, "value": 19.8849},
    ...
  ],
  "volumen": [
    {"time": 1779840000, "value": 3079030400000.0},
    ...
  ]
}
```

> `time` esta en **segundos UTC** (no milisegundos). Para convertir:
> `datetime.fromtimestamp(t, tz=timezone.utc)`.

---

## 16. Historico REPO

**Endpoint:** `GET /api/mercado/titulo/historicorepo?oTitulo={...}`

Historico REPO agrupado por dia, con detalle por **rueda** (REPO, REPX,
SIMU, etc.).

### Parametros `oTitulo`

```json
{"fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05"}
```

### Schema

```json
[
  {
    "fecha": "2026-06-04T00:00:00",
    "volumen": 5076408913172.555,
    "details": [
      {
        "fecha": "2026-06-04T00:00:00",
        "rueda": "REPO",
        "moneda": "$",
        "tasaApertura": 18.0,
        "ultimaTasa": 17.0,
        "tasaMaximo": 20.3,
        "tasaMinimo": 16.0,
        "cierreAyer": 20.0078,
        "cantidad": 3569806000000.0,
        "volumen": 4403093255455.0,
        "tasaPP": 20.0054,
        "variacion": -0.0119,
        "cantOperaciones": 267,
        "plazo": "001",
        "segmento": "7"
      },
      {"rueda": "REPX", "tasaApertura": 19.75, ...},
      {"rueda": "SIMU", ...}
    ]
  }
]
```

### Campos especificos de REPO

| Campo | Descripcion |
|-------|-------------|
| `rueda` | Codigo de rueda: `REPO`, `REPX` (REPO extendido), `SIMU` (Simultaneas), etc. |
| `tasaApertura`, `ultimaTasa`, `tasaMaximo`, `tasaMinimo` | Apertura, cierre, max, min de tasa (% anual). |
| `cierreAyer` | Tasa de cierre del dia anterior. |
| `cantidad` | Cantidad nominal operada. |
| `volumen` | Volumen efectivo en moneda. |
| `tasaPP` | Tasa promedio ponderada. |
| `variacion` | Variacion de tasa vs cierre anterior. |
| `cantOperaciones` | Numero de operaciones cerradas. |
| `segmento` | Codigo de segmento (`7` = principal). |

---

## 17. REPO — volumen y tasa por fecha

**Endpoint:** `GET /api/mercado/repo/titulosfecha?oTitulo={...}`

Serie simplificada de volumen total + tasa promedio ponderada REPO por fecha.

### Parametros `oTitulo`

```json
{"fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05", "unit": "USD"}
```

> ⚠️ El parametro `unit` es **ignorado por la API** — el response es
> identico para `USD`, `ARS`, `$`, `D`, `PESOS`. Se incluye por
> compatibilidad con el frontend del MAE.

### Schema

```json
[
  {
    "fecha": "2026-05-05",
    "volumen": 3152413.955,
    "details": {
      "fecha": "2026-05-05",
      "plazo": 1,
      "volumen": 3152413.955,
      "tPP": 20.61,
      "tPPnBCRA": 21.41
    }
  }
]
```

| Campo | Descripcion |
|-------|-------------|
| `volumen` | Volumen total del dia (probable: miles de millones de pesos). |
| `details.plazo` | Plazo en dias. |
| `details.tPP` | Tasa promedio ponderada del dia. |
| `details.tPPnBCRA` | Tasa promedio ponderada netada del BCRA. |

---

## 18. Indice ARS-MAE — snapshot intradia

**Endpoint:** `GET /api/mercado/indiceARS`

Snapshot de los ultimos 10 puntos intradia del indice ARS-MAE (precio del
dolar mayorista calculado por MAE).

### Schema

```json
[
  {"fecha": "2026-06-04T15:00:00", "tipo": "PBO", "valor": 1437, "valorNuevo": 0},
  {"fecha": "2026-06-04T15:00:00", "tipo": "PPN", "valor": 1438.8159, "valorNuevo": 0}
]
```

| Campo | Descripcion |
|-------|-------------|
| `fecha` | Timestamp del calculo (suele ser cada 1h). |
| `tipo` | `PBO` (Precio Base Operativo) o `PPN` (Precio Promedio Ponderado). |
| `valor` | Valor del indice (precio en pesos del dolar mayorista). |
| `valorNuevo` | Valor de la metodologia nueva (0 si no aplica). |

---

## 19. Indice ARS-MAE — historico diario

**Endpoint:** `GET /api/mercado/titulo/indicearsmae/historico?oTitulo={...}`

Serie historica diaria del cierre del indice ARS-MAE (PPN al cierre).

### Parametros `oTitulo`

```json
{"fechaDesde": "2026-05-05", "fechaHasta": "2026-06-05"}
```

### Schema

```json
[
  {"id": 735, "fecha": "2026-06-04", "valor": 1438.8159, "valorNuevo": 0.0},
  {"id": 733, "fecha": "2026-06-03", "valor": 1435.3812, "valorNuevo": 0.0}
]
```

> Los registros tienen `id` con saltos (no consecutivos) — probable que la
> metodologia genere multiples valores por dia internamente.

---

## 20. Codigos: segmentos, plazos, monedas, ruedas

### Segmentos (`codigoSegmento` / `segmento`)

| Codigo | Descripcion | Aplica a |
|--------|-------------|----------|
| `BT` | Bilateral TRD | Renta Fija (LECAPs, BONCAPs, ONs) |
| `PPT` | Plazo Pesos Transferible | Renta Fija |
| `PT` | Plazo Transferible | Renta Fija |
| `BL` | Bilateral | Renta Fija |
| `TX` | Tomador/Colocador | Renta Fija |
| `RV` | Renta Variable | Acciones (no observado activamente) |
| `EX` | Extranjeras | Cedears, ADRs |
| `M` | Mayorista | FOREX |
| `N` | Minorista | FOREX |
| `K` | Cauciones (Knock-in) | CAARS, CAUSD |
| `DDF` | Dolar Diferido a Fix | DLR062026, DLR072026, ... |
| `7` | REPO segmento principal | REPO |
| `S` | Simultaneas | REPO |

### Plazos (`plazo` / `codigoPlazo`)

| Codigo | Dias | Descripcion |
|--------|------|-------------|
| `000` | 0 | CI (Contado Inmediato) |
| `001` | 1 | 24hs |
| `002` | 2 | 48hs |
| `003` | 3 | 72hs |
| `007` | 7 | 7 dias |
| `014` | 14 | 14 dias |
| `028` | 28 | 28 dias |
| `030` | 30 | 30 dias |

### Monedas (`moneda`)

| Codigo | Descripcion |
|--------|-------------|
| `$` | Pesos argentinos (ARS) |
| `D` | Dolar Bilateral D (similar MEP) |
| `T` | Dolar transferencia mayorista |
| `C` | Dolar Cable (CCL) |

### Ruedas (`rueda` — solo REPO)

| Codigo | Descripcion |
|--------|-------------|
| `REPO` | REPO estandar |
| `REPX` | REPO extendido (plazos largos) |
| `SIMU` | Simultaneas (acuerdos repos simultaneos) |
| `BPBA` | Banco de la Provincia de Buenos Aires (licitaciones) |
| `BNAC` | Banco Nacion (licitaciones) |

### Tipos de emision (`tipoEmision`)

| Codigo | Descripcion |
|--------|-------------|
| `TPN` | Titulo Publico Nacional (bonos, letras Tesoro) |
| `TPP` | Titulo Publico Provincial |
| `ON` | Obligacion Negociable (corporativa) |
| `CAU` | Caucion |
| `FOR` | FOREX (operaciones de moneda) |
| `DDF` | Dolar Diferido a Fix (futuro dolar) |

---

## 21. Manejo de errores

| Status | Significado | Ejemplo de body |
|--------|-------------|-----------------|
| 200 | OK | (response JSON) |
| 400 | Parametro invalido | `{"responseError": 400, "responseMessage": "El estado de la licitacion es incorrecto."}` |
| 404 | Endpoint no existe | (vacio) |
| 500 | Error interno | (vacio o stacktrace) |

### Patrones observados de errores 400

- `resumen/<tipo>` con tipo invalido (cualquier valor distinto de RF, CAU, FOR, DDF).
- `datos/<tipo>` con tipo invalido.
- `licitacionesporestado/Todos` con `estado` no en {A, F, C, S, P}.

### Patrones observados de errores 500

- `datos/DDF` (la API no soporta esta combinacion aunque DDF existe en resumen).
- `flujofondoscotiz/C` (la letra C falla; otras letras retornan `[]` cuando no hay datos).

### Reintentos

La API es estable y rapida (response < 1s tipicamente). Si recibis errores
transitorios (500/503), un retry con backoff exponencial suele resolverlo.

---

## 22. Consideraciones tecnicas

### Rate limiting

No hay rate limiting documentado ni observado. Se recomienda:

- Minimo **0.3 segundos** entre requests.
- En `all` mode el script usa `time.sleep(0.3)` entre cada llamada.
- Evitar batches concurrentes >5 requests simultaneos (no testeado pero
  conservador).

### Delay de los datos

- **Snapshots intradia** (`resumen`, `datos`, `indice-ars`): tiempo real
  con delay estandar de mercado (5-15 min).
- **Historicos** (`hist-*`, `comunicados`): datos T-1 disponibles
  generalmente desde las 19hs ART del dia siguiente.
- **Licitaciones**: actualizadas inmediatamente al cambiar de estado.

### Horarios de actualizacion

- **Rueda RF**: 11:00 - 17:30 ART.
- **Cauciones**: 11:00 - 17:30 ART.
- **FOREX (Mayorista)**: 10:00 - 15:00 ART.
- **REPO**: 11:00 - 16:00 ART.
- **Comunicados**: publicacion durante todo el dia laboral.

### CORS

La API admite requests cross-origin. Util si se usa desde frontend
JavaScript directo, aunque no se recomienda exponer la API a usuarios
finales sin un proxy de cache.

### Cache

No hay headers `Cache-Control` observados. Los snapshots intradia se
actualizan cada ~30s en horario de rueda. Los historicos son estables
(podes cachear `hist-*` por 1 dia).

### Encoding

- API declara `Content-Type: application/json; charset=utf-8`.
- Pero strings con acentos vienen sin UTF-8 valido en algunos campos
  (latin-1 escaped). Recomendado:
  ```python
  import json
  with open("out.json", "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2, ensure_ascii=False)
  ```

### Disponibilidad

- API publica disponible 24/7.
- Los datos solo se actualizan durante horarios de rueda (dias habiles
  argentinos, 10:00-17:30 ART).
- En fines de semana y feriados argentinos los snapshots devuelven los
  datos del ultimo dia habil.

### Aviso legal

- API publica del MAE, sin autenticacion.
- No documentada oficialmente — los endpoints pueden cambiar.
- Respetar terminos de uso del MAE.
- Para uso comercial intensivo, contactar al MAE para licencias formales.

---

## Referencias

- **MAE Oficial:** https://www.mae.com.ar
- **Plataforma Market Data:** https://api.marketdata.mae.com.ar
- **CNV (regulador):** https://www.cnv.gov.ar
- **BCRA (banco central):** https://www.bcra.gob.ar
