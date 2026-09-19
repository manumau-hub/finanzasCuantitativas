# Scanner Columns — Referencia Exhaustiva

> Lista exhaustiva de las **columnas** que se pueden pasar en el array
> `columns: []` del payload `POST /{market}/scan`. El asset estructurado
> esta en [`../assets/scanner_columns.json`](../assets/scanner_columns.json)
> con grupos pre-armados.

**Total verificadas:** 130+ columnas. La API expone ~300+ totales — esta
lista cubre todo lo accionable para finanzas y trading.

---

## Indice

1. [Identidad y metadata](#1-identidad-y-metadata)
2. [Quote basico](#2-quote-basico)
3. [Volumen y volatilidad](#3-volumen-y-volatilidad)
4. [Valuacion](#4-valuacion)
5. [Indicadores tecnicos — osciladores](#5-indicadores-tecnicos--osciladores)
6. [Indicadores tecnicos — medias moviles](#6-indicadores-tecnicos--medias-moviles)
7. [Ratings (Recommend.*)](#7-ratings-recommend)
8. [Pivots mensuales](#8-pivots-mensuales)
9. [Balance sheet](#9-balance-sheet)
10. [Income statement](#10-income-statement)
11. [Cash flow](#11-cash-flow)
12. [Ratios](#12-ratios)
13. [Growth](#13-growth)
14. [Dividendos](#14-dividendos)
15. [Earnings y forecasts](#15-earnings-y-forecasts)
16. [Analyst targets y recommendations](#16-analyst-targets-y-recommendations)
17. [Shares y ownership](#17-shares-y-ownership)
18. [Beta y correlacion](#18-beta-y-correlacion)
19. [Performance returns](#19-performance-returns)
20. [Casos comunes — bundles recomendados](#20-casos-comunes--bundles-recomendados)

---

## 1. Identidad y metadata

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `name` | str | Ticker corto (ej: `GGAL`). NO incluye exchange prefix. |
| `description` | str | Nombre completo del instrumento (ej: `Grupo Financiero Galicia SA Sponsored ADR Class B`) |
| `logoid` | str | ID del logo. URL completa: `https://s3-symbol-logo.tradingview.com/{logoid}--big.svg` |
| `exchange` | str | Exchange code: `NASDAQ`, `NYSE`, `BCBA`, `BME`, `BMFBOVESPA`, etc. |
| `type` | str | `stock`, `dr` (ADR/CEDEAR), `etf`, `fund`, `structured`, `bond`, `crypto`, `forex` |
| `country` | str | Pais del emisor (`Argentina`, `United States`, etc.) |
| `sector` | str | Sector economico (`Finance`, `Technology`, `Energy`, etc.) |
| `industry` | str | Industria especifica (`Regional Banks`, `Software`, etc.) |
| `currency` | str | Moneda de cotizacion (`USD`, `ARS`, `EUR`, `BRL`, `GBP`, etc.) |

---

## 2. Quote basico

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `close` | float | Ultimo precio / cierre |
| `open` | float | Apertura del dia |
| `high` | float | Maximo del dia |
| `low` | float | Minimo del dia |
| `change` | float | Cambio porcentual del dia (en %, no decimal) |
| `change_abs` | float | Cambio absoluto del dia |
| `vwap` | float | Volume-Weighted Average Price |

---

## 3. Volumen y volatilidad

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `volume` | float | Volumen del dia |
| `average_volume_30d_calc` | float | Volumen promedio 30 dias |
| `volume_avg_3m` | float | Volumen promedio 3 meses |
| `volume_change` | float | Cambio % en volumen vs promedio |
| `Volatility.D` | float | Volatilidad diaria % |
| `Volatility.W` | float | Volatilidad semanal % |
| `Volatility.M` | float | Volatilidad mensual % |
| `High.All` | float | Maximo historico (all-time) |
| `Low.All` | float | Minimo historico (all-time) |
| `price_52_week_high` | float | Maximo 52 semanas |
| `price_52_week_low` | float | Minimo 52 semanas |

---

## 4. Valuacion

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `market_cap_basic` | float | Market capitalization (capitalizacion bursatil) |
| `market_cap_calc` | float | Market cap calculada (alternativa) |
| `enterprise_value_fq` | float | Enterprise value trimestre actual |
| `price_earnings_ttm` | float | P/E ratio TTM (trailing twelve months) |
| `price_earnings_to_growth_ratio` | float | PEG ratio |
| `price_sales` | float | P/S ratio |
| `price_book` | float | P/B ratio |
| `price_revenue_ttm` | float | P/Revenue TTM |
| `enterprise_value_ebitda_ttm` | float | EV/EBITDA |
| `enterprise_value_to_revenue_ttm` | float | EV/Revenue |
| `book_value_per_share_fq` | float | Book value per share |
| `earnings_per_share_basic_ttm` | float | EPS basico TTM |
| `earnings_per_share_diluted_ttm` | float | EPS diluido TTM |

---

## 5. Indicadores tecnicos — osciladores

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `RSI` | float | Relative Strength Index (14) |
| `RSI[1]` | float | RSI del periodo anterior |
| `Stoch.K` | float | Stochastic %K |
| `Stoch.D` | float | Stochastic %D |
| `MACD.macd` | float | MACD line |
| `MACD.signal` | float | MACD signal line |
| `ADX` | float | Average Directional Index |
| `ADX+DI` | float | ADX +DI |
| `ADX-DI` | float | ADX -DI |
| `ATR` | float | Average True Range |
| `CCI20` | float | Commodity Channel Index (20) |
| `BBPower` | float | Bull/Bear Power |
| `UO` | float | Ultimate Oscillator |
| `Mom` | float | Momentum |
| `AO` | float | Awesome Oscillator |
| `W.R` | float | Williams %R |

### Interpretacion clave

- **RSI**: 0-100. >70 = sobrecomprado. <30 = sobrevendido.
- **Stoch.K**: 0-100. >80 sobrecomprado. <20 sobrevendido.
- **MACD.macd > MACD.signal**: signal bullish (cross).
- **ADX > 25**: trend fuerte (en cualquier direccion).
- **W.R**: -100 a 0. > -20 sobrecomprado, < -80 sobrevendido.

---

## 6. Indicadores tecnicos — medias moviles

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `SMA10` | float | Simple MA 10 |
| `SMA20` | float | Simple MA 20 |
| `SMA30` | float | Simple MA 30 |
| `SMA50` | float | Simple MA 50 |
| `SMA100` | float | Simple MA 100 |
| `SMA200` | float | Simple MA 200 |
| `EMA10` | float | Exponential MA 10 |
| `EMA20` | float | Exponential MA 20 |
| `EMA30` | float | Exponential MA 30 |
| `EMA50` | float | Exponential MA 50 |
| `EMA100` | float | Exponential MA 100 |
| `EMA200` | float | Exponential MA 200 |
| `VWMA` | float | Volume-Weighted MA |
| `HullMA9` | float | Hull MA (9) |
| `Ichimoku.BLine` | float | Ichimoku Base Line |

### Lectura clasica

- **Golden cross**: `SMA50 > SMA200` (bullish).
- **Death cross**: `SMA50 < SMA200` (bearish).
- **Precio > EMA200**: tendencia largo plazo alcista.
- **Precio > EMA50 > EMA200**: tendencia firme alcista.

---

## 7. Ratings (Recommend.*)

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `Recommend.All` | float [-1, 1] | Rating agregado de TODOS los indicadores |
| `Recommend.MA` | float [-1, 1] | Rating solo de medias moviles |
| `Recommend.Other` | float [-1, 1] | Rating solo de osciladores |

### Mapeo a buckets

| Rango | Bucket | UI label |
|-------|--------|----------|
| -1.00 a -0.50 | `STRONG_SELL` | Venta fuerte |
| -0.50 a -0.10 | `SELL` | Venta |
| -0.10 a +0.10 | `NEUTRAL` | Neutral |
| +0.10 a +0.50 | `BUY` | Compra |
| +0.50 a +1.00 | `STRONG_BUY` | Compra fuerte |

> Asset estructurado en [`../assets/recommend_ratings.json`](../assets/recommend_ratings.json).

---

## 8. Pivots mensuales

Niveles de soporte/resistencia mensuales calculados con 5 metodos
diferentes. Todos en formato `Pivot.M.{METODO}.{NIVEL}`.

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `Pivot.M.Classic.Middle` | float | Pivot point Classic mensual |
| `Pivot.M.Classic.S1` | float | Soporte 1 Classic |
| `Pivot.M.Classic.S2` | float | Soporte 2 Classic |
| `Pivot.M.Classic.S3` | float | Soporte 3 Classic |
| `Pivot.M.Classic.R1` | float | Resistencia 1 Classic |
| `Pivot.M.Classic.R2` | float | Resistencia 2 Classic |
| `Pivot.M.Classic.R3` | float | Resistencia 3 Classic |
| `Pivot.M.Fibonacci.S1` | float | Soporte 1 Fibonacci |
| `Pivot.M.Fibonacci.R1` | float | Resistencia 1 Fibonacci |
| `Pivot.M.Camarilla.S1` | float | Soporte 1 Camarilla |
| `Pivot.M.Camarilla.R1` | float | Resistencia 1 Camarilla |
| `Pivot.M.Woodie.S1` | float | Soporte 1 Woodie |
| `Pivot.M.Woodie.R1` | float | Resistencia 1 Woodie |
| `Pivot.M.DM.S1` | float | Soporte 1 DeMark |
| `Pivot.M.DM.R1` | float | Resistencia 1 DeMark |

> Tambien existen `Pivot.W.{METODO}.{NIVEL}` (semanales) y
> `Pivot.D.{METODO}.{NIVEL}` (diarios) con la misma sintaxis.

---

## 9. Balance sheet

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `total_assets` | float | Activos totales |
| `total_current_assets` | float | Activos corrientes |
| `cash_n_short_term_invest` | float | Cash + inversiones corto plazo |
| `total_debt` | float | Deuda total |
| `long_term_debt` | float | Deuda largo plazo |
| `total_liabilities_fq` | float | Pasivos totales |
| `total_current_liabilities` | float | Pasivos corrientes |
| `total_equity` | float | Equity total |
| `minority_interest` | float | Interes minoritario |

> Todos en moneda del fondo (`currency` field).

---

## 10. Income statement

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `total_revenue` | float | Revenue total TTM |
| `gross_profit` | float | Ganancia bruta |
| `operating_income` | float | Ingreso operativo |
| `net_income` | float | Net income |
| `ebitda` | float | EBITDA |
| `operating_margin` | float | Margen operativo % |
| `gross_margin` | float | Margen bruto % |
| `net_margin` | float | Margen neto % |
| `ebitda_margin` | float | Margen EBITDA % |
| `pre_tax_margin` | float | Margen pre-tax % |

---

## 11. Cash flow

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `free_cash_flow` | float | Free cash flow |
| `cash_f_operating_activities` | float | CF operativo |
| `cash_f_investing_activities` | float | CF inversion |
| `cash_f_financing_activities` | float | CF financiamiento |
| `capital_expenditures` | float | CapEx |

---

## 12. Ratios

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `current_ratio` | float | Activos corrientes / Pasivos corrientes |
| `quick_ratio` | float | (Cash + receivables) / Pasivos corrientes |
| `debt_to_equity` | float | Deuda / Equity |
| `debt_to_assets` | float | Deuda / Activos |
| `return_on_equity` | float | ROE % |
| `return_on_assets` | float | ROA % |
| `return_on_invested_capital` | float | ROIC % |
| `asset_turnover_fy` | float | Asset turnover anual |
| `inventory_turnover_fy` | float | Inventory turnover |

---

## 13. Growth

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `revenue_yoy_growth` | float | Revenue YoY % |
| `revenue_yoy_growth_fy` | float | Revenue YoY anual % |
| `earnings_per_share_diluted_yoy_growth` | float | EPS YoY % |
| `net_income_yoy_growth` | float | Net income YoY % |
| `ebitda_yoy_growth` | float | EBITDA YoY % |

---

## 14. Dividendos

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `dividend_yield_recent` | float | Dividend yield reciente |
| `dividends_yield` | float | Dividend yield TTM |
| `dividends_paid` | float | Dividendos pagados |
| `dps_common_stock_prim_issue_fy` | float | DPS anual |
| `payout_ratio_fy` | float | Payout ratio anual |
| `continuous_dividend_payout` | int | Años consecutivos pagando dividendos |
| `continuous_dividend_growth` | int | Años consecutivos creciendo dividendos |

---

## 15. Earnings y forecasts

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `earnings_release_date` | int (unix) | Fecha ultima earnings |
| `earnings_release_next_date` | int (unix) | Fecha proxima earnings |
| `earnings_release_time` | int | Hora ultima earnings (offset unix) |
| `earnings_release_next_time` | int | Hora proxima earnings (offset unix) |
| `earnings_per_share_fq` | float | EPS reportado trimestre actual |
| `revenue_fq` | float | Revenue reportado trimestre actual |
| `earnings_per_share_forecast_fq` | float | EPS forecast trimestre actual |
| `revenue_forecast_fq` | float | Revenue forecast trimestre actual |
| `earnings_per_share_forecast_next_fq` | float | EPS forecast proximo trimestre |
| `revenue_forecast_next_fq` | float | Revenue forecast proximo trimestre |

> Los `earnings_release_*_date` son timestamps unix (segundos UTC). Convertir
> con `datetime.fromtimestamp(ts, tz=timezone.utc)`.

---

## 16. Analyst targets y recommendations

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `price_target_average` | float | Precio objetivo promedio analistas |
| `price_target_high` | float | Precio objetivo alto |
| `price_target_low` | float | Precio objetivo bajo |
| `price_target_median` | float | Precio objetivo mediano |
| `number_of_analyst_opinions` | int | Cantidad de analistas |
| `recommendation_total` | int | Total recomendaciones |
| `recommendation_buy` | int | Recomendaciones Buy |
| `recommendation_hold` | int | Recomendaciones Hold |
| `recommendation_sell` | int | Recomendaciones Sell |

---

## 17. Shares y ownership

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `float_shares_outstanding` | float | Float (acciones en circulacion) |
| `total_shares_outstanding_fundamental` | float | Acciones totales |
| `shares_outstanding_fundamental_fq` | float | Acciones outstanding trimestre |
| `shares_owned_institutions` | float | Acciones institucionales |
| `shares_owned_insiders` | float | Acciones insiders |
| `short_interest` | float | Short interest |
| `short_interest_percent` | float | Short interest % |
| `days_to_cover_short_interest` | float | Days to cover |

---

## 18. Beta y correlacion

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `beta_1_year` | float | Beta 1 año |
| `beta_3_year` | float | Beta 3 años |
| `beta_5_year` | float | Beta 5 años |
| `correlation_to_sp500_1m` | float | Correlacion S&P 500 1m |

---

## 19. Performance returns

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `Perf.W` | float | Performance semana % |
| `Perf.1M` | float | Performance 1 mes % |
| `Perf.3M` | float | Performance 3 meses % |
| `Perf.6M` | float | Performance 6 meses % |
| `Perf.Y` | float | Performance 1 año % |
| `Perf.YTD` | float | Performance YTD % |
| `Perf.5Y` | float | Performance 5 años % |
| `Perf.All` | float | Performance all-time % |

---

## 20. Casos comunes — bundles recomendados

Bundles pre-armados en [`../assets/column_groups.json`](../assets/column_groups.json).

| Modo CLI | Grupo | # columnas |
|----------|-------|-----------:|
| `quote` | `quote_basic` | 14 |
| `quote-extended` | `quote_extended` | 30 |
| `technicals` | `technicals` | 36 |
| `pivots` | `pivots` | 17 |
| `financials` | `financials` | 35 |
| `earnings` | `earnings` | 12 |
| `targets` | `targets` | 10 |
| `performance` | `performance` | 18 |
| `dividends` | `dividends` | 8 |
| `ownership` | `ownership` | 10 |
| `all` | `all_in_one` | 52 |

### Como agregar columnas custom

```bash
py fetch_tradingview.py quote NASDAQ:GGAL --columns "name,close,RSI,MACD.macd,Recommend.All"
```

O en Python:

```python
from fetch_tradingview import scanner_scan
data = scanner_scan(
    symbols=["NASDAQ:GGAL"],
    columns=["name", "close", "RSI", "MACD.macd", "Recommend.All"],
    market="global",
)
```

---

## Apendice: como descubrir columnas nuevas

TradingView agrega columnas periodicamente. Para descubrir nuevas:

1. Inspeccionar payloads en DevTools del browser sobre `scanner.tradingview.com/{market}/scan`.
2. Probar columnas candidatas. Si retorna `null` para todos los simbolos: probablemente no existe.
3. Reportar via PR en este skill.

Patrones comunes para nombres:
- Tecnicos: `{INDICATOR}` o `{INDICATOR}{PERIOD}` (`RSI`, `EMA50`, `CCI20`)
- Performance: `Perf.{W|1M|3M|...}`
- Pivots: `Pivot.{D|W|M}.{Classic|Fibonacci|Camarilla|Woodie|DM}.{S1|S2|S3|R1|R2|R3|Middle}`
- Earnings: `earnings_*` (snake_case)
- Forecast: `*_forecast_*`
