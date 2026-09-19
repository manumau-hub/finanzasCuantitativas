---
name: alpaca-trading
description: "Trading API de Alpaca: órdenes, posiciones, cuenta. Paper trading y live trading de acciones, crypto y opciones."
license: MIT
---

# Alpaca Trading — Trading API

API para trading de acciones, crypto y opciones. Soporta paper trading (gratis) y live trading.

**Base URLs:**
- Paper: `https://paper-api.alpaca.markets`
- Live: `https://api.alpaca.markets`
- SDK: `pip install alpaca-py`

**Docs:** [docs.alpaca.markets](https://docs.alpaca.markets/us/docs/trading-api)

---

## Autenticación

### Obtener API Keys

1. Ir a [app.alpaca.markets](https://app.alpaca.markets)
2. Crear cuenta (paper trading es gratis)
3. Ir a "API Keys" → Generate New Keys

### Configuración

```python
import os
from alpaca.trading.client import TradingClient

# Para paper trading
API_KEY = os.getenv("APCA_API_KEY_ID")
SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"  # Paper

# Para live trading
# BASE_URL = "https://api.alpaca.markets"

client = TradingClient(API_KEY, SECRET_KEY, paper=True)
```

**⚠️ NUNCA hardcodear keys. Usar variables de entorno.**

---

## Rate Limits

| API | Límite |
|-----|--------|
| Orders | 200 requests/min |
| Account/Positions | 200 requests/min |
| Account Activities | 200 requests/min |

### Recomendaciones

- **Usar WebSocket para updates en tiempo real** — más eficiente que polling
- **Cachear account/positions** — no consultar constantemente
- **Implementar retry con exponential backoff** para 429 errors

---

## Account

### Obtener Información de Cuenta

```python
account = client.get_account()
print(f"Buying Power: ${account.buying_power}")
print(f"Cash: ${account.cash}")
print(f"Portfolio Value: ${account.portfolio_value}")
print(f"Status: {account.status}")
```

### Configuración de Cuenta

```python
from alpaca.trading.requests import AccountConfigurationsRequest

config_request = AccountConfigurationsRequest(
    trade_confirmation_email=True,
    susi_transfer_email=True
)
client.update_account_configuration(config_request)
```

---

## Assets

### Listar Todos los Assets

```python
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass, AssetStatus

request = GetAssetsRequest(
    asset_class=AssetClass.US_EQUITY,
    status=AssetStatus.ACTIVE
)

assets = client.get_all_assets(request)

# Filtrar symbols tradables
tradable = [a for a in assets if a.tradable]
print(f"Assets tradables: {len(tradable)}")
```

### Obtener Asset Específico

```python
asset = client.get_asset("AAPL")
print(f"AAPL tradable: {asset.tradable}")
print(f"AAPL class: {asset.asset_class}")
```

---

## Orders

### Tipos de Órdenes

| Tipo | Descripción |
|------|-------------|
| `market` | Ejecuta al precio actual |
| `limit` | Precio máximo (buy) o mínimo (sell) |
| `stop` | Activa orden de mercado cuando alcanza stop_price |
| `stop_limit` | Combina stop + limit |
| `trailing_stop` | Stop relativo al precio |

### Time in Force

| TIF | Descripción |
|-----|-------------|
| `day` | Solo para día actual |
| `gtc` | Good Till Cancelled |
| `opg` | Open at market open |
| `cls` | Close at market close |
| `ioc` | Immediate Or Cancel |
| `fok` | Fill Or Kill |

### Crear Orden de Market

```python
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

order_request = MarketOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
)

order = client.submit_order(order_request)
print(f"Order ID: {order.id}")
print(f"Status: {order.status}")
```

### Crear Orden Limit

```python
from alpaca.trading.requests import LimitOrderRequest

order_request = LimitOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.BUY,
    limit_price=150.00,  # Máximo a pagar
    time_in_force=TimeInForce.GTC
)

order = client.submit_order(order_request)
```

### Crear Orden Stop

```python
from alpaca.trading.requests import StopOrderRequest

order_request = StopOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.SELL,
    stop_price=145.00,  # Vende cuando caiga a este precio
    time_in_force=TimeInForce.GTC
)
```

### Obtener Órdenes

```python
# Todas las órdenes abiertas
open_orders = client.get_orders(status="open")
print(f"Órdenes abiertas: {len(open_orders)}")

# Órdenes filladas hoy
from datetime import datetime
filled_orders = client.get_orders(
    status="fill",
    start=datetime(2024, 1, 15)
)

# Orden por ID
order = client.get_order_by_id(order_id)
```

### Cancelar Órdenes

```python
# Cancelar una orden
client.cancel_order(order_id)

# Cancelar todas las órdenes abiertas
client.cancel_orders()
```

### Reemplazar Orden

```python
from alpaca.trading.requests import ReplaceOrderRequest

replace_request = ReplaceOrderRequest(
    limit_price=155.00,  # Nuevo precio límite
    qty=15               # Nueva cantidad
)
client.replace_order(order_id, replace_request)
```

---

## Positions

### Obtener Posiciones Abiertas

```python
positions = client.get_all_positions()

for pos in positions:
    print(f"{pos.symbol}: {pos.qty} shares")
    print(f"  Avg Entry: ${pos.avg_entry_price}")
    print(f"  Market Value: ${pos.market_value}")
    print(f"  P/L: ${pos.unrealized_pl}")
```

### Obtener Posición Específica

```python
position = client.get_position("AAPL")
print(f"AAPL: {position.qty} shares @ ${position.avg_entry_price}")
```

### Cerrar Posición

```python
# Cerrar toda la posición
client.close_position("AAPL")

# Cerrar posición parcialmente (qty=5)
client.close_position("AAPL", qty=5)
```

### Cerrar Todas las Posiciones

```python
client.close_all_positions()
```

---

## Options Trading

### Trading Levels

| Level | Descripción |
|-------|-------------|
| 0 | Sin trading de opciones |
| 1 | Covered calls, cash-secured puts |
| 2 | Buy/sell calls y puts |
| 3 | Spreads |

### Obtener Option Contracts

```python
from alpaca.trading.requests import GetOptionContractsRequest
from datetime import datetime, timedelta

request = GetOptionContractsRequest(
    underlying_symbols=["AAPL"],
    expiration_date_gte=datetime.now().strftime("%Y-%m-%d"),
    expiration_date_lte=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    strike_price_gte=100,
    strike_price_lte=200,
    limit=100
)

contracts = client.get_option_contracts(request)
contract = contracts.option_contracts[0]

# Trade con contract ID
order_request = MarketOrderRequest(
    symbol=contract.id,  # Usar ID del contract
    qty=1,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
)
```

### Ejercitar Opción

```python
# Ejercer una posición de opción
client.exercise_options(position_id)
```

---

## Crypto Trading

### Listar Symbols Disponibles

```python
from alpaca.trading.enums import AssetClass

crypto_assets = client.get_all_assets(asset_class=AssetClass.CRYPTO)
crypto = [a for a in crypto_assets if a.tradable]
print(f"Crypto tradables: {[a.symbol for a in crypto[:10]]}")
```

### Órdenes de Crypto

```python
order_request = MarketOrderRequest(
    symbol="BTC/USD",
    qty=0.1,  # Fracciones permitidas
    side=OrderSide.BUY,
    time_in_force=TimeInForce.GTC
)
client.submit_order(order_request)
```

---

## Market Hours

### Obtener Clock

```python
clock = client.get_clock()
print(f"Market open: {clock.is_open}")
print(f"Next open: {clock.next_open}")
print(f"Next close: {clock.next_close}")
```

### Verificar si Mercado está Abierto

```python
if clock.is_open:
    print("Mercado abierto - puedes tradear")
else:
    print("Mercado cerrado")
```

---

## Portfolio History

```python
from datetime import datetime

history = client.get_account_portfolio_history(
    date_start=datetime(2024, 1, 1),
    timeframe="1D"
)

print(f"Equity: {history.equity}")
print(f"Profit/Loss: {history.profit_loss}")
```

---

## Watchlists

```python
from alpaca.trading.requests import CreateWatchlistRequest

# Crear watchlist
watchlist = client.create_watchlist(
    CreateWatchlistRequest(name="Tech Stocks")
)

# Agregar símbolo
client.add_to_watchlist(watchlist.id, "AAPL")

# Obtener watchlists
watchlists = client.get_watchlists()
```

---

## WebSocket Streaming

```python
from alpaca.trading.stream import TradingStream

async def handle_trade_update(data):
    print(f"Update: {data}")

stream = TradingStream(API_KEY, SECRET_KEY, paper=True)

stream.subscribe_trade_updates(handle_trade_update)
stream.run()
```

---

## Scripts de Ejemplo

Ver [./scripts/](./scripts/):

```bash
# Ver cuenta
python ./scripts/check_account.py

# Ver posiciones
python ./scripts/check_positions.py

# Enviar orden de prueba
python ./scripts/place_order.py --symbol AAPL --qty 10 --side buy --type market
```

---

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 403 Forbidden | Keys inválidas | Verificar API keys |
| 403 | Sin permisos | Habilitar en dashboard |
| 400 Bad Request | Parámetros inválidos | Ver docs de orden |
| 403 Trading Halted | Trading pausado | Esperar o verificar |
| 403 No Buying Power | Sin fondos | Depositar dinero |
| 422 | Symbol no tradable | Verificar symbol |
| 429 Too Many Requests | Rate limit | Implementar backoff |

---

## Comparación: Paper vs Live

| Aspecto | Paper | Live |
|---------|-------|------|
| URL | paper-api.alpaca.markets | api.alpaca.markets |
| Dinero real | ❌ No | ✅ Sí |
| Órdenes reales | ❌ Simuladas | ✅ Reales |
| Datos de mercado | ✅ Reales | ✅ Reales |
| Para testing | ✅ Ideal | ❌ No |

**Siempre probar en paper primero.**
