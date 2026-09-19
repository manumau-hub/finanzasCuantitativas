---
name: primary
description: "Trading API de Primary (Matba ROFEX): futuros, opciones, acciones, bonos. Órdenes, posiciones, cuenta, market data."
license: MIT
---

# Primary — Trading API de Matba ROFEX

API para operar en el Mercado Argentino de Futuros y Opciones (Matba ROFEX) a través de Primary Trading Platform (PTP). Soporta futuros (dólar, soja, trigo, maíz, índices), opciones sobre futuros, acciones, bonos y CEDEARs.

**Base URL:** `https://api.remarkets.primary.com.ar`

**Docs:** [github.com/matbarofex](https://github.com/matbarofex/) — repositorio oficial con ejemplos open source.

---

## Autenticación

### Obtener Credenciales

| Entorno | URL | Descripción |
|---------|-----|-------------|
| **REMARKET** (demo) | [remarkets.primary.ventures](https://remarkets.primary.ventures/) | Crear cuenta gratis para paper trading |
| **LIVE** (producción) | Contactar a [mpi@primary.com.ar](mailto:mpi@primary.com.ar) | Solicitar acceso al equipo MPI |

Una vez creada la cuenta en REMARKET, tendrás:
- **Usuario**: el que registraste
- **Password**: el que configuraste
- **Account**: tu número de cuenta (suele ser `REM` + últimos dígitos del usuario)

### Obtener Token

```python
import requests

r = requests.post("https://api.remarkets.primary.com.ar/auth/getToken",
    headers={"X-Username": tu_usuario, "X-Password": tu_password})

token = r.headers["X-Auth-Token"]
```

El token se envía en adelante como header `X-Auth-Token` en todos los requests.

**⚠️ NUNCA hardcodear credenciales. Usar variables de entorno o parámetros CLI.**

```python
import os
TOKEN = os.getenv("PRIMARY_TOKEN")  # Opcional: cachear token
USER = os.getenv("PRIMARY_USER")
PASS = os.getenv("PRIMARY_PASSWORD")
ACCOUNT = os.getenv("PRIMARY_ACCOUNT")  # Ej: 12345 o REM12345
```

### Renew Token

Si recibís un 401, el token expiró. Renovalo con un nuevo POST a `/auth/getToken`.

---

## Segmentos

El mercado se organiza en **segmentos** (ruedas de negociación). Cada instrumento pertenece a un segmento.

| Segmento | Descripción |
|----------|-------------|
| `DDF` | Derivados Financieros (futuros de dólar, índices) |
| `DDA` | Derivados Agropecuarios (soja, trigo, maíz) |
| `DUAL` | Instrumentos listados en ambas divisiones |
| `MERV` | Mercados externos a Matba ROFEX (BYMA) |
| `MAE` | Mercado Abierto Electrónico |
| `TEST` | Ambiente de pruebas |
| `U-DDF`, `U-DDA`, `U-DUAL`, `U-FIN`, `U-COMM`, `U-STOCK` | Sub-segmentos de usuarios |
| `TIVA`, `AVS` | Otros segmentos |

### Listar Segmentos

```http
GET https://api.remarkets.primary.com.ar/rest/segment/all
```

```python
r = requests.get("https://api.remarkets.primary.com.ar/rest/segment/all",
    headers={"X-Auth-Token": token})
print(r.json()["segments"])
```

**Respuesta:**
```json
{"status":"OK","segments":[
  {"marketSegmentId":"DDF","marketId":"ROFX"},
  {"marketSegmentId":"DDA","marketId":"ROFX"},
  ...
]}
```

---

## Instrumentos (Securities)

Los instrumentos se identifican por su **símbolo** y **marketId**. Ejemplos:

| Símbolo | Descripción | CFI Code |
|---------|-------------|----------|
| `DLR/JUN26` | Futuro de dólar Junio 2026 | `FXXXSX` |
| `SOJ.ROS/MAY26` | Futuro de soja Rosario Mayo 2026 | `FXXXSX` |
| `DLR/JUN26 1460 C` | Opción Call sobre futuro dólar | `OCAFXS` |
| `DLR/JUN26 1420 P` | Opción Put sobre futuro dólar | `OPAFXS` |
| `GGAL` | Acción Grupo Galicia | `ESXXXX` |

### Todos los Instrumentos

```http
GET https://api.remarkets.primary.com.ar/rest/instruments/all
```

### Instrumentos con Detalle

```http
GET https://api.remarkets.primary.com.ar/rest/instruments/details
```

Devuelve: `symbol`, `segment`, `lowLimitPrice`, `highLimitPrice`, `minPriceIncrement`, `minTradeVol`, `maxTradeVol`, `tickSize`, `contractMultiplier`, `roundLot`, `maturityDate`, `currency`, `orderTypes`, `timesInForce`, `cficode`.

### Detalle de un Instrumento

```http
GET https://api.remarkets.primary.com.ar/rest/instruments/detail?symbol=DLR/JUN26&marketId=ROFX
```

### Por Código CFI

```http
GET https://api.remarkets.primary.com.ar/rest/instruments/byCFICode?CFICode=FXXXSX
```

| CFI Code | Tipo |
|----------|------|
| `FXXXSX` | Futuro |
| `FXXXXX` | Futuro (genérico) |
| `OCAFXS` | Opción Call sobre Futuro |
| `OPAFXS` | Opción Put sobre Futuro |
| `OCEFXS` | Opción Call europea sobre Futuro |
| `OPEFXS` | Opción Put europea sobre Futuro |
| `ESXXXX` | Acción |
| `DBXXXX` | Bono |
| `EMXXXX` | CEDEAR |
| `OCASPS` | Opción Call sobre Acción |
| `OPASPS` | Opción Put sobre Acción |
| `DBXXFR` | Obligación Negociable |

### Por Segmento

```http
GET https://api.remarkets.primary.com.ar/rest/instruments/bySegment?MarketSegmentID=DDF&MarketID=ROFX
```

---

## Market Data

### En Tiempo Real (REST Snapshot)

```http
GET https://api.remarkets.primary.com.ar/rest/marketdata/get
    ?marketId=ROFX
    &symbol=DLR/JUN26
    &entries=BI,OF,LA,OP,CL,SE,OI
    &depth=3
```

| Entry | Significado |
|-------|-------------|
| `BI` | Bids (ofertas de compra en el book) |
| `OF` | Offers (ofertas de venta en el book) |
| `LA` | Last (último precio operado) |
| `OP` | Opening Price (precio de apertura) |
| `CL` | Closing Price (cierre rueda anterior) |
| `SE` | Settlement Price (precio de ajuste, solo futuros) |
| `HI` | High Price (máximo de la rueda) |
| `LO` | Low Price (mínimo de la rueda) |
| `TV` | Trade Volume (volumen operado en contratos) |
| `OI` | Open Interest (interés abierto, solo futuros) |
| `IV` | Index Value (solo índices) |
| `EV` | Effective Volume (solo BYMA) |
| `NV` | Nominal Volume (solo BYMA) |
| `ACP` | Auction Price (cierre del día corriente) |

```python
r = requests.get("https://api.remarkets.primary.com.ar/rest/marketdata/get",
    headers={"X-Auth-Token": token},
    params={"marketId": "ROFX", "symbol": "DLR/JUN26",
            "entries": "BI,OF,LA,OP,CL,SE,OI", "depth": 3})
data = r.json()["marketData"]
print(f"Bid: {data['BI']}  |  Offer: {data['OF']}")
print(f"Last: {data['LA']}  |  Settle: {data['SE']}")
```

### Histórica (Trades)

```http
GET https://api.remarkets.primary.com.ar/rest/data/getTrades
    ?marketId=ROFX
    &symbol=DLR/JUN26
    &dateFrom=2026-06-01
    &dateTo=2026-06-08
```

Parámetros: `marketId`, `symbol`, `date` (una fecha), `dateFrom`/`dateTo` (rango), `external` (para mercados externos), `environment` (`REMARKETS`).

```python
r = requests.get("https://api.remarkets.primary.com.ar/rest/data/getTrades",
    headers={"X-Auth-Token": token},
    params={"marketId": "ROFX", "symbol": "DLR/JUN26",
            "date": "2026-06-05"})
trades = r.json()["trades"]
for t in trades[:3]:
    print(f"{t['datetime']}  {t['price']}  {t['size']}")
```

---

## Órdenes

### Tipos de Órdenes

| Tipo | Descripción |
|------|-------------|
| `LIMIT` | Orden con precio límite |
| `MARKET` | Orden a mercado |
| `STOP_LIMIT` | Orden stop que se activa como limit |
| `MARKET_TO_LIMIT` | Market que se convierte en limit |

*Nota: STOP_LIMIT y MARKET_TO_LIMIT no están disponibles para todos los instrumentos. Verificar `orderTypes` en el detalle del instrumento.*

### Time in Force (TIF)

| TIF | Descripción |
|-----|-------------|
| `DAY` | Solo válida por el día. Se expira al cierre de rueda |
| `IOC` | Immediate or Cancel |
| `FOK` | Fill or Kill |
| `GTD` | Good Till Date (requiere `expireDate`) |

### Ingresar Orden (REST)

```http
GET https://api.remarkets.primary.com.ar/rest/order/newSingleOrder
    ?marketId=ROFX
    &symbol=DLR/JUN26
    &side=BUY
    &orderQty=10
    &ordType=LIMIT
    &price=1450.0
    &timeInForce=DAY
    &account=TU_CUENTA
    &cancelPrevious=False
    &iceberg=False
```

**Parámetros:**

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|:-----------:|-------------|
| `marketId` | String | ✅ | `ROFX` |
| `symbol` | String | ✅ | Símbolo del instrumento |
| `side` | String | ✅ | `BUY` o `SELL` |
| `orderQty` | Integer | ✅ | Cantidad de contratos |
| `ordType` | String | ✅ | `LIMIT` o `MARKET` |
| `price` | Float | Condicional | Requerido para LIMIT |
| `timeInForce` | String | No | `DAY` (default), `IOC`, `FOK`, `GTD` |
| `account` | Integer/String | ✅ | Número de cuenta |
| `cancelPrevious` | Boolean | No | Cancela órdenes previas del mismo contrato/lado |
| `iceberg` | Boolean | No | Orden Iceberg (default: false) |
| `displayQty` | Integer | Condicional | Cantidad a divulgar (para iceberg) |
| `expireDate` | Date | Condicional | Requerido para GTD (formato: YYYYMMDD) |

**Respuesta:**
```json
{"status":"OK","order":{"clientId":"21581341758","proprietary":"PBCP"}}
```

El `clientId` es el **clOrdId** (Client Order ID) que se usa para consultar/cancelar la orden.

### Ingresar Orden (WebSocket)

```json
{"type":"no","product":{"marketId":"ROFX","symbol":"DLR/JUN26"},
 "price":185,"quantity":23,"side":"BUY","account":"20","iceberg":false}
```

Para identificar la orden vía WebSocket, incluir `wsClOrdId`:
```json
{"type":"no","product":{"marketId":"ROFX","symbol":"DLR/JUN26"},
 "price":185,"quantity":23,"side":"BUY","account":"20",
 "iceberg":false,"wsClOrdId":"mioid-unico-123"}
```

**Respuesta WebSocket (Execution Report):**
```json
{"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545...",
 "status":"PENDING_NEW","text":"Enviada","wsClOrdId":"mioid-unico-123"}}
```

> **Importante:** El `wsClOrdId` solo aparece en el primer execution report. Luego se debe usar el `clOrdId` devuelto para seguimiento.

### Reemplazar Orden

```http
GET https://api.remarkets.primary.com.ar/rest/order/replaceById
    ?clOrdId=user144733478280357
    &proprietary=api
    &price=17
    &orderQty=10
```

### Cancelar Orden

```http
GET https://api.remarkets.primary.com.ar/rest/order/cancelById
    ?clOrdId=ajduj3l13ieci2jr4ck
    &proprietary=PBCP
```

### Cancelar por WebSocket

```json
{"type":"co","clientId":"user114121092035207","proprietary":"PBCP"}
```

### Consultar Estado de la Orden (REST)

| Endpoint | Descripción |
|----------|-------------|
| `GET /rest/order/id?clOrdId=...&proprietary=api` | Último estado del request |
| `GET /rest/order/allById?clOrdId=...&proprietary=api` | Todos los estados del request |
| `GET /rest/order/byOrderId?orderId=...` | Estado por Order ID |
| `GET /rest/order/actives?accountId=10` | Órdenes activas (NEW o PARTIALLY_FILLED) |
| `GET /rest/order/filleds?accountId=10` | Órdenes total o parcialmente operadas |
| `GET /rest/order/all?accountId=10` | Todos los estados de la cuenta |
| `GET /rest/order/byExecId?execId=T1234567` | Estado por Execution ID |

### Execution Reports (WebSocket)

Suscribirse a una cuenta:
```json
{"type":"os","account":{"id":"40"}}
```

Varias cuentas:
```json
{"type":"os","accounts":[{"id":"40"},{"id":"4000"}]}
```

Todas las cuentas:
```json
{"type":"os"}
```

Solo órdenes activas:
```json
{"type":"os","snapshotOnlyActive":true}
```

---

## Risk API

La Risk API usa **HTTP Basic Auth** con el mismo user/password, no token. Requiere el header `Authorization: Basic <base64>` adicionalmente al `X-Auth-Token`.

```python
import base64
auth = base64.b64encode(f"{user}:{password}".encode()).decode()
headers = {"X-Auth-Token": token, "Authorization": f"Basic {auth}"}
```

### Posiciones de una Cuenta

```http
GET https://api.remarkets.primary.com.ar/rest/risk/position/getPositions/{accountName}
```

```python
r = requests.get(f"https://api.remarkets.primary.com.ar/rest/risk/position/getPositions/TU_CUENTA",
    headers=headers)
positions = r.json()["positions"]
for p in positions:
    print(f"{p['symbol']}  Buy:{p['buySize']}  Sell:{p['sellSize']}  Diff:{p['totalDiff']}")
```

### Posiciones Detalladas

```http
GET https://api.remarkets.primary.com.ar/rest/risk/detailedPosition/{accountName}
```

Devuelve desglose por instrumento con: `contractType`, `marketPrice`, `currency`, `exchangeRate`, `contractMultiplier`, `buyCurrentSize`, `sellCurrentSize`, `detailedDailyDiff`.

### Reporte de Cuenta

```http
GET https://api.remarkets.primary.com.ar/rest/risk/accountReport/{accountName}
```

```python
import base64
auth = base64.b64encode(f"{user}:{password}".encode()).decode()
headers = {"X-Auth-Token": token, "Authorization": f"Basic {auth}"}
r = requests.get(f"https://api.remarkets.primary.com.ar/rest/risk/accountReport/TU_CUENTA",
    headers=headers)
data = r.json()["accountData"]
print(f"Colateral: {data['collateral']}")
print(f"Margen: {data['margin']}")
print(f"Disponible: {data['availableToCollateral']}")
# Saldos por moneda
for moneda, saldo in data['detailedAccountReports']['0']['currencyBalance']['detailedCurrencyBalance'].items():
    print(f"  {moneda}: consumido={saldo['consumed']}  disponible={saldo['available']}")
```

---

## WebSocket

**URL:** `wss://api.remarkets.primary.com.ar/`

La API WebSocket recibe mensajes asíncronos. El token se envía como **header** en la conexión:

```python
import websocket

ws = websocket.WebSocketApp(
    "wss://api.remarkets.primary.com.ar/",
    header=[f"X-Auth-Token: {token}"],
    on_open=on_open,
    on_message=on_message,
    ...
)
ws.run_forever()
```

Los mensajes tienen el formato:

| type | Significado |
|------|-------------|
| `no` | New Order (enviar orden) |
| `co` | Cancel Order (cancelar orden) |
| `or` | Order Report (execution report recibido) |
| `os` | Order Subscription (suscribirse a reports) |
| `smd` | Subscribe Market Data |
| `Md` | Market Data (recibido) |

### Market Data por WebSocket

```json
{"type":"smd","level":1,"entries":["OF","BI","LA"],
 "products":[{"symbol":"DLR/JUN26","marketId":"ROFX"}],"depth":2}
```

Respuesta:
```json
{"type":"Md","instrumentId":{"marketId":"ROFX","symbol":"DLR/JUN26"},
 "marketData":{"OF":[{"price":189,"size":21},{"price":188,"size":13}]}}
```

---

## Estados de una Orden

| Estado | Significado |
|--------|-------------|
| `PENDING_NEW` | Enviada al mercado, aún no procesada |
| `NEW` | Aceptada, activa en el book |
| `PARTIALLY_FILLED` | Parcialmente operada |
| `FILLED` | Totalmente operada |
| `CANCELLED` | Cancelada |
| `REJECTED` | Rechazada (ver `text` para motivo) |
| `PENDING_CANCEL` | Cancelación en proceso |
| `PENDING_REPLACE` | Reemplazo en proceso |
| `REPLACED` | Reemplazada |
| `PENDING_APPROVAL` | Pendiente de aprobación |

---

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 401 Unauthorized | Token inválido o expirado | Renovar con `/auth/getToken` |
| `"No tiene acceso a la cuenta"` | Account ID incorrecto | Verificar `accountId` |
| `"Product doesn't exist"` | Symbol incorrecto | Verificar símbolo con `instruments/all` |
| `"Access Denied"` | Sin permisos para el endpoint | Verificar segmento/método |
| `"Ruta invalida"` | Endpoint no existe | Revisar URL |
| Bid/Offer vacíos | Mercado cerrado o sin liquidez | Consultar en horario de rueda |

---

## Scripts de Ejemplo

Ver [./scripts/](./scripts/):

```bash
# Autenticación y token (opcional, los scripts hacen login automático)
export PRIMARY_USER="tu_usuario"
export PRIMARY_PASSWORD="tu_password"
export PRIMARY_ACCOUNT="TU_CUENTA"

# Listar segmentos e instrumentos
python scripts/instruments.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD

# Market data de un futuro
python scripts/market_data.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --symbol DLR/JUN26 --entries BI,OF,LA

# Ver reporte de cuenta
python scripts/check_account.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --account TU_CUENTA

# Ver posiciones
python scripts/check_positions.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --account TU_CUENTA

# Enviar orden (¡cuidado! orden real en live)
python scripts/place_order.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --symbol DLR/JUN26 --side BUY --qty 1 --type LIMIT --price 1450 --account TU_CUENTA

# WebSocket: Market Data en tiempo real
python scripts/websocket_md.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --symbols DLR/JUN26 --entries BI,OF,LA --depth 3

# WebSocket: Execution Reports
python scripts/websocket_orders.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --account TU_CUENTA

# WebSocket: Enviar orden (requiere suscripción a execution reports aparte)
python scripts/websocket_send_order.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --symbol DLR/JUN26 --side BUY --qty 1 --type LIMIT --price 1450 --account TU_CUENTA

# WebSocket: Cancelar orden
python scripts/websocket_send_order.py --user $PRIMARY_USER --password $PRIMARY_PASSWORD \
    --cancel --clordid user12345... --proprietary PBCP
```

---

## Glosario de Campos

| Campo | Descripción |
|-------|-------------|
| `clOrdId` | Client Order ID — ID del request al mercado |
| `orderId` | Order ID — ID de la orden en el mercado |
| `execId` | Execution ID — ID de una ejecución particular |
| `proprietary` | Usuario FIX que envió la orden (`PBCP` o `ISV_PBCP`) |
| `wsClOrdId` | ID de orden enviada por WebSocket (solo en 1er report) |
| `avgPx` | Precio promedio operado |
| `cumQty` | Cantidad acumulada operada |
| `leavesQty` | Cantidad remanente |
| `lastPx` | Último precio operado |
| `lastQty` | Última cantidad operada |
| `transactTime` | Fecha y hora de la transacción |
| `tickSize` | Incremento mínimo de cantidad |
| `minPriceIncrement` | Incremento mínimo de precio (tick price) |
| `contractMultiplier` | Multiplicador del contrato |
| `maturityDate` | Fecha de vencimiento |
| `priceConvertionFactor` | Factor para precio unitario |
| `lowLimitPrice` | Límite mínimo de precio |
| `highLimitPrice` | Límite máximo de precio |
