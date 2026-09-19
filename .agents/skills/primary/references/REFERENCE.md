---
name: primary
description: "API Reference — Primary Trading Platform (Matba ROFEX). Compiled from live API testing on 2026-06-08."
---

# Primary API — Reference Document

> Documentación de referencia generada a partir de pruebas directas contra la API de Primary (Matba ROFEX).
> Entorno: REMARKET (`https://api.remarkets.primary.com.ar`)

---

## Índice

1. [Autenticación](#1-autenticación)
2. [Segmentos](#2-segmentos)
3. [Instrumentos](#3-instrumentos)
   - 3.1. Resumen por CFI Code
   - 3.2. Resumen por Segmento
   - 3.3. Detalle de un Instrumento (DLR/JUN26)
   - 3.4. Campos del detalle
4. [Market Data](#4-market-data)
   - 4.1. Entries disponibles
   - 4.2. Snapshot DLR/JUN26 (con datos)
   - 4.3. Snapshot DLR/JUL26 (con datos)
   - 4.4. Snapshot DLR/AGO26 (sin liquidez)
5. [Trades Históricos](#5-trades-históricos)
6. [Órdenes](#6-órdenes)
   - 6.1. Endpoints de consulta
   - 6.2. Envío de orden (newSingleOrder)
7. [Risk API](#7-risk-api)
   - 7.1. Account Report
   - 7.2. Posiciones
   - 7.3. Posiciones Detalladas
8. [Errores](#8-errores)
9. [Glosario de Campos de Respuesta](#9-glosario-de-campos-de-respuesta)

---

## 1. Autenticación

| Método | Endpoint | Headers requeridos | Response |
|--------|----------|--------------------|----------|
| POST | `/auth/getToken` | `X-Username`, `X-Password` | Header `X-Auth-Token` |

- El token tiene una vigencia de **24 horas**.
- Enviar en adelante como header `X-Auth-Token` en todos los requests.
- **Risk API** requiere además `Authorization: Basic <base64>`.

```
Token obtenido: jiRCar5sB7vr7ufmV3gIqCZ8r2pWFzWahFUrIAG0vlU=
Longitud: 44 caracteres
```

---

## 2. Segmentos

**Endpoint:** `GET /rest/segment/all`

Total: **19 segmentos**

| # | Segmento | Market ID | Descripción |
|---|----------|-----------|-------------|
| 1 | `DDA` | ROFX | Derivados Agropecuarios |
| 2 | `DDF` | ROFX | Derivados Financieros |
| 3 | `DUAL` | ROFX | Listados en ambas divisiones |
| 4 | `TEST` | ROFX | Ambiente de pruebas |
| 5 | `MAE` | ROFX | Mercado Abierto Electrónico |
| 6 | `MERV` | ROFX | Mercados externos (BYMA) |
| 7 | `MVR` | ROFX | — |
| 8 | `MVC` | ROFX | — |
| 9 | `MATBA` | ROFX | — |
| 10 | `MVM` | ROFX | — |
| 11 | `U-DDA` | ROFX | Sub-segmento usuarios DDA |
| 12 | `U-DDF` | ROFX | Sub-segmento usuarios DDF |
| 13 | `U-DUAL` | ROFX | Sub-segmento usuarios DUAL |
| 14 | `U-DDF-S` | ROFX | — |
| 15 | `U-FIN` | ROFX | — |
| 16 | `U-COMM` | ROFX | — |
| 17 | `U-STOCK` | ROFX | — |
| 18 | `TIVA` | ROFX | — |
| 19 | `AVS` | ROFX | — |

---

## 3. Instrumentos

### 3.1. Resumen por CFI Code

**Endpoint:** `GET /rest/instruments/all`

Total: **1360 instrumentos**

| CFI Code | Tipo | Cantidad | Ejemplos |
|----------|------|:--------:|----------|
| `ESXXXX` | Acción | 22 | SUPV, YPFDD, GGALD, GGAL, TXAR, PAMP |
| `DBXXXX` | Bono | 490 | AL41, GD30C, GD41, AL30, AL29, AE38 |
| `EMXXXX` | CEDEAR | 10 | AAPLD, BBD, KO, SPYD, SPY |
| `FXXXSX` | Futuro | 135 | DLR/JUN26, SOJ.ROS/NOV26, TRI.ROS/DIC26, MAI.ROS/JUL26 |
| `FXXXXX` | Futuro (spread) | 35 | SOJ.ROS/JUL26/MAY27, MAI.ROS/JUL26/DIC26 |
| `OCAFXS` | Call sobre Futuro | 200 | SOJ.ROS/NOV26 360 C, TRI.ROS/DIC26 212 C |
| `OCEFXS` | Call europea sobre Futuro | 10 | DLR/JUN26 1430 C, DLR/JUN26 1460 C |
| `OPAFXS` | Put sobre Futuro | 151 | MAI.ROS/JUL26 200 P, TRI.ROS/JUL26 200 P |
| `OPEFXS` | Put europea sobre Futuro | 5 | DLR/AGO25 1376 P, DLR/AGO25 1368 P |
| `OCASPS` | Call sobre Acción | 3 | — |
| `OPASPS` | Put sobre Acción | 1 | — |
| `DBXXFR` | ON (Obligación Negociable) | 250 | — |
| `MCXXXX` | Moneda / Crypto | 6 | USDT.MEP, USDC, ActivoDePrueba |
| `DTXXXX` | — | 2 | — |
| `DXXXXX` | — | 6 | — |
| `DYXTXR` | — | 2 | — |
| `MRIXXX` | — | 15 | — |
| `MXXXXX` | — | 2 | — |
| `RPXXXX` | — | 15 | — |

### 3.2. Resumen por Segmento

**Endpoint:** `GET /rest/instruments/bySegment?MarketSegmentID={seg}&MarketID=ROFX`

| Segmento | Cantidad | Ejemplos |
|----------|:--------:|----------|
| `DDF` | 55 | DLR/JUN26, DLR/JUN26 1460 C, DLR/JUN26/JUL26 |
| `DDA` | 447 | SOJ.ROS/NOV26 360 C, TRI.ROS/JUL26 200 P |
| `DUAL` | 40 | CAUC/AGO26, TMR/JUN26, AL30D/JUN26 |
| `MERV` | 59 | AL41, SUPV, GGALD, YPFDD, AL30, AL29 |
| `MAE` | 14 | CAARS/5D, CAARS/4D, CAARS/3D |
| `TEST` | 11 | I.RFX20_TEST, ZVZZTC2.0, ZVZZT |

### 3.3. Detalle de un Instrumento

**Endpoint:** `GET /rest/instruments/detail?symbol=DLR/JUN26&marketId=ROFX`

```json
{
  "status": "OK",
  "instrument": {
    "symbol": null,
    "segment": { "marketSegmentId": "DDF", "marketId": "ROFX" },
    "lowLimitPrice": 1307.0,
    "highLimitPrice": 1607.0,
    "minPriceIncrement": 0.5,
    "minTradeVol": 1.0,
    "maxTradeVol": 10000.0,
    "tickSize": 1.0,
    "contractMultiplier": 1000.0,
    "roundLot": 1.0,
    "priceConvertionFactor": 1.0,
    "maturityDate": "20260630",
    "currency": "ARS",
    "orderTypes": ["STOP_LIMIT", "MARKET_TO_LIMIT", "LIMIT"],
    "timesInForce": ["IOC", "DAY", "GTD"],
    "instrumentPricePrecision": 1,
    "instrumentSizePrecision": 0,
    "securityDescription": "DLR/JUN26",
    "tickPriceRanges": { "0": { "lowerLimit": 0, "upperLimit": null, "tick": 0.5 } },
    "strike": null,
    "underlying": "Dólar USA A3500",
    "cficode": "FXXXSX",
    "instrumentId": { "marketId": "ROFX", "symbol": "DLR/JUN26" }
  }
}
```

### 3.4. Campos del Detalle

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `instrumentId.symbol` | String | Símbolo del instrumento |
| `instrumentId.marketId` | String | `ROFX` |
| `segment.marketSegmentId` | String | `DDF`, `DDA`, etc. |
| `segment.marketId` | String | `ROFX` |
| `cficode` | String | Código CFI |
| `securityDescription` | String | Descripción |
| `maturityDate` | String (YYYYMMDD) | Vencimiento |
| `currency` | String | `ARS`, `USD`, `USDG` |
| `contractMultiplier` | Float | Multiplicador (DLR=1000) |
| `minPriceIncrement` | Float | Tick de precio |
| `minTradeVol` | Float | Volumen mínimo |
| `maxTradeVol` | Float | Volumen máximo |
| `lowLimitPrice` | Float | Precio mínimo |
| `highLimitPrice` | Float | Precio máximo |
| `tickSize` | Float | Incremento de cantidad |
| `roundLot` | Float | Lote redondo |
| `priceConvertionFactor` | Float | Factor de conversión |
| `orderTypes` | List | Tipos de orden soportados |
| `timesInForce` | List | TIFs soportados |
| `instrumentPricePrecision` | Integer | Decimales del precio |
| `instrumentSizePrecision` | Integer | Decimales de cantidad |
| `securityType` | String | Tipo de security (usualmente null) |
| `settlType` | String | Tipo de liquidación (usualmente null) |
| `underlying` | String | Subyacente (para futuros/opciones) |
| `strike` | Float | Strike (para opciones) |
| `tickPriceRanges` | Object | Rangos de ticks dinámicos |

---

## 4. Market Data

### 4.1. Entries Disponibles

| Entry | Significado | Estructura |
|-------|-------------|------------|
| `BI` | Bids (ofertas de compra) | `[{price, size}, ...]` |
| `OF` | Offers (ofertas de venta) | `[{price, size}, ...]` |
| `LA` | Last (último precio operado) | `{price, size, date}` |
| `OP` | Opening Price (apertura) | Float |
| `CL` | Closing Price (cierre anterior) | `{price, size, date}` o null |
| `SE` | Settlement (ajuste, solo futuros) | `{price, size, date}` |
| `HI` | High Price (máximo rueda) | Float |
| `LO` | Low Price (mínimo rueda) | Float |
| `TV` | Trade Volume (volumen contratos) | Integer |
| `OI` | Open Interest (interés abierto) | `{price, size, date}` |
| `IV` | Index Value (solo índices) | Float |
| `EV` | Effective Volume (solo BYMA) | Integer |
| `NV` | Nominal Volume (solo BYMA) | Integer |
| `ACP` | Auction Price (cierre corriente) | Float |

### 4.2. Snapshot DLR/JUN26 (con liquidez)

**Endpoint:** `GET /rest/marketdata/get?marketId=ROFX&symbol=DLR/JUN26&entries=BI,OF,LA,OP,CL,SE,OI,HI,LO,TV&depth=3`

```json
{
  "status": "OK",
  "marketData": {
    "CL": null,
    "OI": null,
    "LO": 1471.0,
    "OF": [],
    "OP": 1471.5,
    "SE": { "price": 1457.0, "size": null, "date": 1780617600000 },
    "LA": { "price": 1480.0, "size": 1, "date": 1780882745423 },
    "BI": [{"price": 1450.0, "size": 3}],
    "HI": 1480.0,
    "TV": 3
  },
  "depth": 3,
  "aggregated": true
}
```

- Settlement Price: **1457.0**
- Last Price: **1480.0** (size 1)
- Bid: **1450.0** (size 3)
- Offer: vacío (mercado cerrado)
- Open Interest: null
- High: 1480.0 / Low: 1471.0

### 4.3. Snapshot DLR/JUL26

```json
{
  "marketData": {
    "OP": 1499.5,
    "SE": { "price": 1485.0 },
    "LA": { "price": 1482.5, "size": 1 },
    "BI": [{"price": 1400.0, "size": 2}],
    "HI": 1499.5,
    "TV": 3
  }
}
```

### 4.4. Snapshot DLR/AGO26 (sin liquidez)

```json
{
  "marketData": {
    "SE": { "price": 1514.5 },
    "LA": null,
    "BI": [],
    "OF": [],
    "TV": 0
  }
}
```

Solo tiene Settlement Price. Sin bids, sin offers, sin trades. Mercado sin liquidez en esta fecha.

---

## 5. Trades Históricos

**Endpoint:** `GET /rest/data/getTrades?marketId=ROFX&symbol=DLR/JUN26&date=2026-06-05`

| Atributo | Valor |
|----------|-------|
| Símbolo | DLR/JUN26 |
| Fecha | 2026-06-05 |
| Total trades | 2285 |
| Rango precio | 1453.50 — 1464.00 |
| Volumen total | 283,136 contratos |

**Primeros 3 trades:**

```json
[
  {"symbol": "DLR/JUN26", "servertime": 1780665005478, "size": 100.0, "price": 1457.5, "datetime": "2026-06-05 13:10:05.478"},
  {"symbol": "DLR/JUN26", "servertime": 1780665005478, "size": 10.0,  "price": 1457.5, "datetime": "2026-06-05 13:10:05.478"},
  {"symbol": "DLR/JUN26", "servertime": 1780665013519, "size": 190.0, "price": 1457.5, "datetime": "2026-06-05 13:10:13.519"}
]
```

---

## 6. Órdenes

### 6.1. Endpoints de Consulta

| Endpoint | Parámetros | Resultado en test |
|----------|------------|-------------------|
| `GET /rest/order/actives?accountId={id}` | accountId | 0 órdenes |
| `GET /rest/order/filleds?accountId={id}` | accountId | 0 órdenes |
| `GET /rest/order/all?accountId={id}` | accountId | 0 órdenes |

Sin órdenes activas ni operadas al momento del test.

### 6.2. Envío de Orden (newSingleOrder)

No se testearon envíos reales de orden. Ver `SKILL.md` y `scripts/place_order.py` para parámetros y ejemplos.

---

## 7. Risk API

Requiere **HTTP Basic Auth** adicional al token.

### 7.1. Account Report

**Endpoint:** `GET /rest/risk/accountReport/{accountName}`

**Ejemplo de respuesta (cuenta de prueba):**

| Campo | Valor |
|-------|-------|
| Market Member | PrimaryVenture |
| Identity | PMYVTR |
| Colateral | 0.00 |
| Margen | 0.00 |
| Disponible para colateral | ARS 114,565,800.00 |
| Portfolio Value | 0.00 |
| Daily Diff | 0.00 |
| Current Cash | ARS 114,565,800.00 |
| Uncovered Margin | 0.00 |

**Saldos por moneda:**

| Moneda | Consumido | Disponible |
|--------|:---------:|:----------:|
| ARS | 0.00 | 100,000,000.00 |
| USD D | 0.00 | 10,000.00 |
| USD MtR | 0.00 | 0.00 |
| USD G | 0.00 | 0.00 |
| USD R | 0.00 | 0.00 |
| USD C | 0.00 | 0.00 |
| U$S | 0.00 | 0.00 |
| EUR | 0.00 | 0.00 |
| UYU | 0.00 | 0.00 |
| USD UY | 0.00 | 0.00 |
| ARS BCRA | 0.00 | 0.00 |

**Disponible para operar:**

| Concepto | ARS |
|----------|:--------:|
| Total Cash | 114,565,800.00 |
| Movements | 0.00 |
| Credit | null |
| Total Operable | 114,565,800.00 |

### 7.2. Posiciones

**Endpoint:** `GET /rest/risk/position/getPositions/{accountName}`

Devuelve lista de posiciones abiertas. Cada posición contiene:

- `symbol`: símbolo del instrumento
- `buySize` / `sellSize`: cantidad comprada/vendida
- `buyPrice` / `sellPrice`: precio promedio de compra/venta
- `totalDiff`: diferencia total
- `totalDailyDiff`: diferencia diaria

### 7.3. Posiciones Detalladas

**Endpoint:** `GET /rest/risk/detailedPosition/{accountName}`

Devuelve desglose por tipo de instrumento (`FUTURE`, `FUTURE_OPTION_CALL`, etc.) con detalle de precios de mercado, moneda, tipo de cambio, y diferencias diarias.

---

## 8. Errores

| Escenario | HTTP | Response |
|-----------|:----:|----------|
| Token inválido | 401 | `{"status":"ERROR","message":"Unauthorized"}` |
| Cuenta sin acceso | 200 | `{"status":"ERROR","message":"Access Denied.","description":"You don't have access to account NOEXISTE"}` |
| Símbolo inexistente | 200 | `{"status":"ERROR","description":"Security ZZZZZ:ROFX doesn't exist"}` |
| Ruta inválida | 200 | `{"status":"ERROR","message":"Invalid URL","description":"Invalid URL"}` |

Todos los errores de la API devuelven HTTP **200** excepto errores de autenticación (HTTP **401**).

---

## 9. Glosario de Campos de Respuesta

Campos identificados en las respuestas reales de la API:

| Campo | Tipo | Aparece en | Descripción |
|-------|------|-----------|-------------|
| `status` | String | Todos | `"OK"` o `"ERROR"` |
| `message` | String | Errores | Mensaje de error |
| `description` | String | Errores | Descripción del error |
| `segments` | List | segment/all | Lista de segmentos |
| `segment` | Object | instruments | `{marketSegmentId, marketId}` |
| `instruments` | List | instruments/* | Lista de instrumentos |
| `instrument` | Object | instruments/detail | Detalle de un instrumento |
| `instrumentId` | Object | instruments, orders | `{marketId, symbol}` |
| `marketId` | String | Varios | `"ROFX"` |
| `marketSegmentId` | String | Varios | `"DDF"`, `"DDA"`, etc. |
| `symbol` | String | Varios | Símbolo del instrumento |
| `cficode` | String | instruments | Código CFI |
| `securityDescription` | String | instruments/detail | Descripción |
| `maturityDate` | String | instruments/detail | Vencimiento (YYYYMMDD) |
| `currency` | String | instruments/detail | `ARS`, `USD`, `USDG` |
| `contractMultiplier` | Float | instruments/detail | Multiplicador |
| `minPriceIncrement` | Float | instruments/detail | Tick de precio |
| `minTradeVol` | Float | instruments/detail | Vol. mínimo |
| `maxTradeVol` | Float | instruments/detail | Vol. máximo |
| `lowLimitPrice` | Float | instruments/detail | Precio mínimo |
| `highLimitPrice` | Float | instruments/detail | Precio máximo |
| `tickSize` | Float | instruments/detail | Incremento cantidad |
| `roundLot` | Float | instruments/detail | Lote |
| `priceConvertionFactor` | Float | instruments/detail | Factor conversión |
| `orderTypes` | List | instruments/detail | `["LIMIT","STOP_LIMIT","MARKET_TO_LIMIT"]` |
| `timesInForce` | List | instruments/detail | `["DAY","IOC","GTD"]` |
| `instrumentPricePrecision` | Integer | instruments/detail | Decimales precio |
| `instrumentSizePrecision` | Integer | instruments/detail | Decimales cantidad |
| `tickPriceRanges` | Object | instruments/detail | Rangos de ticks |
| `underlying` | String | instruments/detail | Subyacente |
| `strike` | Float | instruments/detail | Strike (opciones) |
| `marketData` | Object | marketdata/get | Datos de mercado |
| `depth` | Integer | marketdata/get | Profundidad devuelta |
| `aggregated` | Boolean | marketdata/get | `true` |
| `BI` | List | marketData | Bids |
| `OF` | List | marketData | Offers |
| `LA` | Object/null | marketData | Last |
| `OP` | Float/null | marketData | Opening |
| `CL` | Object/null | marketData | Closing |
| `SE` | Object/null | marketData | Settlement |
| `HI` | Float/null | marketData | High |
| `LO` | Float/null | marketData | Low |
| `TV` | Integer | marketData | Volumen |
| `OI` | Object/null | marketData | Open Interest |
| `price` | Float | marketData entries | Precio |
| `size` | Float | marketData entries | Tamaño |
| `date` | Long | marketData entries | Timestamp |
| `trades` | List | data/getTrades | Lista de trades |
| `servertime` | Long | trades | Timestamp del trade |
| `datetime` | String | trades | Fecha-hora del trade |
| `orders` | List | order/* | Lista de órdenes |
| `orderId` | String/null | orders | ID de orden |
| `clOrdId` | String | orders | Client Order ID |
| `execId` | String | orders | Execution ID |
| `proprietary` | String | orders | `"PBCP"` o `"ISV_PBCP"` |
| `accountId` | Object | orders | `{id: "10"}` |
| `avgPx` | Float | orders | Precio promedio |
| `lastPx` | Float | orders | Último precio |
| `lastQty` | Integer | orders | Última cantidad |
| `cumQty` | Integer | orders | Cantidad acumulada |
| `leavesQty` | Integer | orders | Cantidad remanente |
| `transactTime` | String | orders | Fecha-hora transacción |
| `text` | String | orders | Texto del estado |
| `accountData` | Object | risk/accountReport | Datos de cuenta |
| `accountName` | String | risk | Nombre de cuenta |
| `marketMember` | String | risk | Miembro de mercado |
| `marketMemberIdentity` | String | risk | Identidad |
| `collateral` | Float | risk | Colateral |
| `margin` | Float | risk | Margen |
| `availableToCollateral` | Float | risk | Disponible |
| `portfolio` | Float | risk | Valor cartera |
| `currentCash` | Float | risk | Efectivo |
| `dailyDiff` | Float | risk | Diferencia diaria |
| `uncoveredMargin` | Float | risk | Margen descubierto |
| `detailedAccountReports` | Object | risk | Detalle por moneda |
| `currencyBalance` | Object | risk | Balance por moneda |
| `availableToOperate` | Object | risk | Disponible para operar |
| `positions` | List | risk/position | Posiciones |
| `buySize` | Integer | positions | Cantidad comprada |
| `sellSize` | Integer | positions | Cantidad vendida |
| `buyPrice` | Float | positions | Precio de compra |
| `sellPrice` | Float | positions | Precio de venta |
| `totalDiff` | Float | positions | Diferencia total |
| `totalDailyDiff` | Float | positions | Diferencia diaria |
| `detailedPosition` | Object | risk/detailed | Posición detallada |
| `report` | Object | risk/detailed | Reporte por tipo |

---

*Documento generado el 2026-06-08 mediante pruebas directas contra `api.remarkets.primary.com.ar`.*
