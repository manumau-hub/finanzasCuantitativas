# Options Reference — Alpaca Data

## Símbolos de Opciones

Los símbolos de opciones de Alpaca siguen el formato:
```
{UNDERLYING}{DATE}{TYPE}{STRIKE}{100}
```

### Ejemplo

```
AAPL240119C00100000
├── AAPL    = Underlying symbol (6 chars)
├── 240119  = Fecha: 24 Jan 19 (YYMMDD)
├── C       = Type: C (Call) o P (Put)
├── 00100   = Strike price x 1000 (100.00)
└── 000     = Padding
```

## Parámetros de Filtrado

### expiration_date

```python
request = OptionContractsRequest(
    underlying_symbols=["AAPL"],
    expiration_date_gte="2024-01-01",  # Desde (inclusive)
    expiration_date_lte="2024-12-31",  # Hasta (inclusive)
)
```

### strike_price

```python
request = OptionContractsRequest(
    underlying_symbols=["AAPL"],
    strike_price_gte=100,   # Mínimo 100
    strike_price_lte=200,   # Máximo 200
)
```

### type

```python
request = OptionContractsRequest(
    underlying_symbols=["AAPL"],
    type="call"  # "call" o "put"
)
```

### style

```python
request = OptionContractsRequest(
    underlying_symbols=["AAPL"],
    style="american"  # American o European
)
```

## Trading Levels Requeridos

| Level | Trades Permitidos |
|-------|------------------|
| 0 | Sin trading de opciones |
| 1 | Covered calls, cash-secured puts |
| 2 | Buy/Sell calls y puts |
| 3 | Call/put spreads |

## Obtener Option Chain Completa

```python
from datetime import datetime, timedelta

# Fechas de expiración
min_exp = datetime.now()
max_exp = datetime.now() + timedelta(days=365)

request = OptionContractsRequest(
    underlying_symbols=["AAPL"],
    expiration_date_gte=min_exp.strftime("%Y-%m-%d"),
    expiration_date_lte=max_exp.strftime("%Y-%m-%d"),
    strike_price_gte=50,
    strike_price_lte=300,
    limit=1000  # Max 100 por request
)

contracts = client.get_option_contracts(request)
```

## Parsear Símbolo de Contrato

```python
def parse_option_symbol(symbol: str) -> dict:
    """Parse AAPL240119C00100000 -> {underlying, exp, type, strike}"""
    underlying = symbol[:6].strip()
    date_str = symbol[6:12]
    exp_type = symbol[12]
    strike = symbol[13:18]
    
    year = "20" + date_str[:2]
    month = date_str[2:4]
    day = date_str[4:6]
    
    return {
        "underlying": underlying,
        "expiration": f"{year}-{month}-{day}",
        "type": "Call" if exp_type == "C" else "Put",
        "strike": int(strike) / 1000
    }

# Ejemplo
info = parse_option_symbol("AAPL240119C00100000")
print(info)
# {'underlying': 'AAPL', 'expiration': '2024-01-19', 'type': 'Call', 'strike': 100.0}
```

## Ejemplo: Obtener Todas las Calls para AAPL

```python
from datetime import datetime
import pandas as pd

request = OptionContractsRequest(
    underlying_symbols=["AAPL"],
    expiration_date_gte=datetime.now().strftime("%Y-%m-%d"),
    type="call",
    limit=1000
)

contracts = client.get_option_contracts(request)

# Convertir a DataFrame
df = pd.DataFrame([{
    "symbol": c.symbol,
    "strike": float(c.strike_price),
    "expiration": c.expiration_date,
    "type": c.type,
    "style": c.style,
    "open_interest": int(c.open_interest) if c.open_interest else 0
} for c in contracts.option_contracts])

df = df.sort_values(["expiration", "strike"])
print(df.head(20))
```
