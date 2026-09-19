# Technical Indicators Reference

Endpoint base: `https://www.alphavantage.co/query`

Parámetros comunes:
- `function`: Nombre del indicador (ej: RSI, SMA)
- `symbol`: Símbolo de la acción
- `interval`: Temporalidad (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)
- `time_period`: Período de cálculo
- `apikey`: Tu API key

## Trend Indicators

| Indicator | Description |
|-----------|-------------|
| SMA | Simple Moving Average |
| EMA | Exponential Moving Average |
| WMA | Weighted Moving Average |
| DEMA | Double Exponential Moving Average |
| TEMA | Triple Exponential Moving Average |
| TRIMA | Triangular Moving Average |
| KAMA | Kaufman's Adaptive Moving Average |
| MAMA | MESA Adaptive Moving Average |
| T3 | Triple Exponential Moving Average (T3) |

## Momentum Indicators

| Indicator | Description |
|-----------|-------------|
| RSI | Relative Strength Index |
| MACD | Moving Average Convergence/Divergence |
| STOCH | Stochastic Oscillator |
| STOCHRSI | Stochastic Relative Strength Index |
| WILLiams%R | Williams %R |
| ADX | Average Directional Movement Index |
| ADXR | Average Directional Movement Index Rating |
| APO | Absolute Price Oscillator |
| PPO | Percentage Price Oscillator |
| MOM | Momentum |
| ROC | Rate of Change |
| ROCR | Rate of Change Ratio |
| CCI | Commodity Channel Index |
| MFI | Money Flow Index |
| AROON | Aroon |
| AROONOSC | Aroon Oscillator |
| DX | Directional Movement Index |

## Volatility Indicators

| Indicator | Description |
|-----------|-------------|
| BBANDS | Bollinger Bands |
| ATR | Average True Range |
| NATR | Normalized Average True Range |
| TRANGE | True Range |

## Volume Indicators

| Indicator | Description |
|-----------|-------------|
| OBV | On Balance Volume |
| AD | Chaikin A/D Line |
| ADOSC | Chaikin Oscillator |
| ADL | Accumulation/Distribution |

## Hilbert Transform Indicators

| Indicator | Description |
|-----------|-------------|
| HT_TRENDLINE | Hilbert Transform Instantaneous Trendline |
| HT_SINE | Hilbert Transform Sine Wave |
| HT_PHASOR | Hilbert Transform Phase |
| HT_QUADRAVTURE | Hilbert Transform Quadrature |
| HT_DCPERIOD | Hilbert Transform Dominant Cycle Period |
| HT_DCPHASE | Hilbert Transform Dominant Cycle Phase |
| HT_TRENDMODE | Hilbert Transform Trend vs Cycle Mode |

## Other Indicators

| Indicator | Description |
|-----------|-------------|
| VWAP | Volume Weighted Average Price |
| SAR | Parabolic SAR |
| MIDPOINT | MidPoint over period |
| MIDPRICE | Midpoint Price over period |
| VWMAP | Volume Weighted Moving Average |

## Ejemplo de Uso

```python
import requests

url = "https://www.alphavantage.co/query"
params = {
    "function": "RSI",
    "symbol": "IBM",
    "interval": "weekly",
    "time_period": 14,
    "series_type": "close",
    "apikey": "TU_API_KEY"
}

r = requests.get(url, params=params)
data = r.json()
```
