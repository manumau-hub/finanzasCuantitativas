# Finviz Quote Page — Referencia de Campos

Documentación de los campos extraídos de `finviz.com/quote.ashx?t=TICKER`.

---

## Campos Fundamentales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Market Cap` | string | Capitalización de mercado (ej: "1,234.5B") |
| `P/E` | string | Price-to-Earnings ratio (ttm) |
| `Forward P/E` | string | Forward Price-to-Earnings |
| `PEG` | string | PEG ratio (P/E / growth) |
| `P/S` | string | Price-to-Sales |
| `P/B` | string | Price-to-Book |
| `EPS (ttm)` | string | Earnings Per Share trailing 12 months |
| `EPS next Y` | string | Estimated EPS next year |
| `EPS next Q` | string | Estimated EPS next quarter |
| `EPS this Y` | string | EPS growth this year |
| `EPS next Y` | string (show) | EPS growth next year |
| `Sales` | string | Total revenue |
| `Profit Margin` | string | Profit margin percentage |
| `ROE` | string | Return on Equity |
| `ROA` | string | Return on Assets |
| `ROI` | string | Return on Investment |
| `Debt/Eq` | string | Debt-to-Equity ratio |
| `Dividend %` | string | Dividend yield |
| `Dividend` | string | Dividend amount per share |
| `Dividend date` | string | Next dividend date |
| `Payout` | string | Payout ratio |
| `Insider Own` | string | Insider ownership % |
| `Instit Own` | string | Institutional ownership % |
| `Insider Trans` | string | Insider transactions (net) |
| `Inst Trans` | string | Institutional transactions (net) |
| `Short Float` | string | Short float % |
| `Short Ratio` | string | Short ratio (days to cover) |
| `Target Price` | string | Analyst mean target price |
| `Rating` | string | Analyst consensus rating |
| `RSI (14)` | string | Relative Strength Index (14-day) |
| `Employees` | string | Number of employees |
| `Optionable` | string | Yes/No |
| `Shs Outstand` | string | Shares outstanding |
| `Shs Float` | string | Shares float |
| `Prev Close` | string | Previous closing price |
| `Price` | string | Current price |
| `Change` | string | Price change |
| `Volume` | string | Trading volume |
| `Avg Volume` | string | Average volume |
| `52W High` | string | 52-week high |
| `52W Low` | string | 52-week low |
| `SMA 20` | string | Simple Moving Average 20 days |
| `SMA 50` | string | Simple Moving Average 50 days |
| `SMA 200` | string | Simple Moving Average 200 days |
| `50-Day` | string | 50-day average |
| `200-Day` | string | 200-day average |
| `Perf Week` | string | Performance this week |
| `Perf Month` | string | Performance this month |
| `Perf Quarter` | string | Performance this quarter |
| `Perf Half Y` | string | Performance half year |
| `Perf Year` | string | Performance this year |
| `Perf YTD` | string | Performance year-to-date |
| `Beta` | string | Beta (5-year monthly) |
| `ATR` | string | Average True Range |
| `Volatility` | string | Volatility (week/month) |
| `MACD` | string | MACD value |
| `BB` | string | Bollinger Bands value |
| `20-Day` | string | 20-day simple moving average |
| `50-Day` | string | 50-day simple moving average |
| `200-Day` | string | 200-day simple moving average |
| `RSI` | string | Relative Strength Index |
| `Gap` | string | Gap (open vs prev close) |
| `Pattern` | string | Candlestick pattern |
| `CCI` | string | Commodity Channel Index |
| `StochRSI` | string | Stochastic RSI |
| `ROC` | string | Rate of Change |
| `Williams %R` | string | Williams %R |
| `Ultimate` | string | Ultimate Oscillator |
| `ADX` | string | Average Directional Index |
| `WMA` | string | Weighted Moving Average |
| `DEM` | string | DeMarker |
| `5-Day SMA` | string | Simple Moving Average 5 days |
| `10-Day SMA` | string | Simple Moving Average 10 days |
| `30-Day SMA` | string | Simple Moving Average 30 days |
| `60-Day SMA` | string | Simple Moving Average 60 days |
| `100-Day SMA` | string | Simple Moving Average 100 days |
| `LT Debt/Eq` | string | Long-term Debt-to-Equity |
| `EPS past 5Y` | string | EPS growth past 5 years |
| `EPS next 5Y` | string | EPS growth next 5 years |
| `Sales past 5Y` | string | Sales growth past 5 years |
| `Quick Ratio` | string | Quick ratio |
| `Current Ratio` | string | Current ratio |
| `Gross Margin` | string | Gross margin |
| `Oper. Margin` | string | Operating margin |
| `Pre-tax Margin` | string | Pre-tax margin |
| `P/C` | string | Price-to-Cash |
| `P/FCF` | string | Price-to-Free Cash Flow |
| `EPS` | string | Earnings Per Share |
| `F过一个` | string | Earnings per share next year |
| `Recom` | string | Recommendation (analyst consensus) |
| `SMA20` | string | Simple Moving Average (20) |
| `SMA50` | string | Simple Moving Average (50) |
| `SMA200` | string | Simple Moving Average (200) |
| `52W High` | string | 52-week high price |
| `52W Low` | string | 52-week low price |
| `RSI` | string | Relative Strength Index |
| `ATR` | string | Average True Range |
| `BB` | string | Bollinger Band |
| `MACD` | string | MACD |
| `Earnings` | string | Next earnings date |
| `Option/Short` | string | Optionable + Shortable |

> **Nota:** Los nombres de campos pueden variar ligeramente si Finviz actualiza su interfaz. El scraper extrae los labels exactos tal como aparecen en la página.

---

## Estructura del Output JSON

```json
{
  "ticker": "AAPL",
  "fundamentals": {
    "Market Cap": "2,850.4B",
    "P/E": "28.45",
    "Forward P/E": "27.10",
    "EPS (ttm)": "6.47",
    ...
  },
  "technicals": {
    "RSI (14)": "65.4",
    "SMA 20": "182.50",
    "SMA 50": "178.30",
    "SMA 200": "165.20",
    ...
  },
  "news": [
    {
      "date": "Jun 02 06:30AM",
      "title": "Apple Hits New High on AI Optimism",
      "url": "https://...",
    }
  ],
  "insider_trading": [
    {
      "trader": "COOK TIMOTHY D",
      "relationship": "CEO",
      "date": "May 30",
      "transaction": "Sale",
      "cost": "180.50",
      "shares": "50,000"
    }
  ]
}
```
