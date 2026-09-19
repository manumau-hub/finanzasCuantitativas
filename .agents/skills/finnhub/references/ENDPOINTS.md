# Finnhub API — Referencia Completa de Endpoints

Documentación detallada de todos los endpoints de la API de Finnhub, indicando **claramente cuáles son gratuitos** y cuáles requieren plan pago.

**Base URL:** `https://finnhub.io/api/v1`  
**Auth:** `?token=API_KEY` (query param) o header `X-Finnhub-Token: API_KEY`  
**Formato:** JSON  
**Rate limit general:** 30 calls/segundo (aplica a todos los planes)

---

## Leyenda

| Símbolo | Significado |
|---------|-------------|
| ✅ **FREE** | Confirmado funcionando en plan gratuito (60 calls/min) |
| ✅ *FREE (no test)* | Documentado como free pero no pudo verificarse con key gratuita |
| 🔒 **PREMIUM** | Requiere plan pago (Starter $11.99/mes, Professional $49.99/mes o Enterprise) |

> ⚠️ **Nota importante:** Esta documentación está basada en **pruebas reales con una API key gratuita en junio 2026**. El plan gratuito de Finnhub es significativamente más limitado de lo que su documentación general sugiere. Solo 10 endpoints funcionan en free. Los endpoints marcados como "FREE (no test)" están documentados como gratuitos por Finnhub pero no pudieron ser verificados con la key disponible.

---

## 1. Stock Market Data

### GET /quote — Cotización en Tiempo Real ✅ FREE

Precio actual, cambio, apertura, máximo, mínimo, cierre anterior. **Confirmado funcionando.**

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `symbol` | ✅ | Símbolo (ej: AAPL) |

**Respuesta:**
```json
{
  "c": 150.25,    // Precio actual
  "d": -2.50,     // Cambio
  "dp": -1.63,    // Cambio %
  "h": 153.00,    // Máximo del día
  "l": 149.50,    // Mínimo del día
  "o": 152.00,    // Apertura
  "pc": 152.75,   // Cierre anterior
  "t": 1717459200 // Timestamp UNIX
}
```

---

### GET /stock/candle — Velas OHLCV Históricas 🔒 PREMIUM

Datos históricos de velas. **Requiere plan pago** (Starter+). Plan gratuito no tiene acceso (devuelve 403).

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `symbol` | ✅ | Símbolo (ej: AAPL) |
| `resolution` | ✅ | `1`, `5`, `15`, `30`, `60`, `D`, `W`, `M` |
| `from` | ✅ | Timestamp UNIX inicio |
| `to` | ✅ | Timestamp UNIX fin |

---

### GET /stock/profile2 — Perfil de Empresa v2 ✅ FREE

Información general de una empresa. **Confirmado funcionando.**

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `symbol` | ✅ | Símbolo (ej: AAPL) |

**Respuesta:**
```json
{
  "country": "US",
  "currency": "USD",
  "exchange": "NASDAQ NMS - GLOBAL MARKET",
  "finnhubIndustry": "Technology",
  "ipo": "1980-12-12",
  "logo": "https://...",
  "marketCapitalization": 2800000,
  "name": "Apple Inc",
  "shareOutstanding": 15500,
  "ticker": "AAPL",
  "weburl": "https://www.apple.com/"
}
```

---

### GET /stock/peers — Empresas Similares ✅ FREE

Retorna lista de tickers de empresas comparables. **Confirmado funcionando.**

| Parámetro | Requerido |
|-----------|-----------|
| `symbol` | ✅ |

---

### GET /stock/market-status — Estado del Mercado ✅ FREE

Indica si un mercado está abierto/cerrado. **Confirmado funcionando.**

| Parámetro | Requerido |
|-----------|-----------|
| `exchange` | ✅ |

---

### GET /stock/market-holiday — Calendario de Feriados ✅ FREE (no test)

| Parámetro | Requerido |
|-----------|-----------|
| `exchange` | ✅ |

---

### GET /stock/symbol — Listado de Símbolos ✅ FREE (no test)

| Parámetro | Requerido |
|-----------|-----------|
| `exchange` | ✅ |

---

## 2. Datos Fundamentales

### GET /stock/metric — Métricas Financieras Clave ✅ FREE

Retorna **~130-150 métricas financieras** (133 confirmado en AAPL) en una sola llamada. **No es histórico** — solo devuelve el valor actual/más reciente de cada métrica (sin serie temporal).

| Parámetro | Requerido |
|-----------|-----------|
| `symbol` | ✅ |
| `metric` | ❌ (`all`=todas, `price`, `valuation`, `margin`, `profitability`) |

**Métricas agrupadas por categoría (testeado con AAPL en free):**

| Categoría | Cantidad | Ejemplos |
|-----------|:--------:|----------|
| Rentabilidad y Márgenes | ~19 | grossMargin, netProfitMargin, operatingMargin, ROE, ROA, pretaxMargin |
| Per-Share | ~18 | bookValuePerShare, cashFlowPerShare, tangibleBookValuePerShare |
| Ingresos y Earnings | ~15 | revenueGrowth, ebitdaCagr, revenuePerShare, netIncomeEmployee |
| Valuación | ~11 | enterpriseValue, forwardPE, forwardPEG, marketCapitalization |
| Ratios por Período | ~21 | currentRatio, quickRatio, payoutRatio, pegTTM, psTTM |
| Price Return / Momentum | ~7 | 52WeekHigh/Low, 52WeekPriceReturnDaily |
| Trading Volume Corto | ~4 | 10DayAvgVolume, 3MonthAvgVolume |
| Balance | ~6 | assetTurnover, inventoryTurnover, receivablesTurnover |
| Dividendos | ~6 | currentDividendYieldTTM, dividendGrowthRate5Y |
| Crecimiento | ~4 | epsGrowth3Y/5Y, epsGrowthQuarterlyYoy |
| Otras | ~20 | pe, pb, ps, eps (varios), debt/equity, netInterestCoverage |

**Las métricas incluyen múltiples frecuencias en la misma respuesta:**
- **TTM** (Trailing Twelve Months): `peTTM`, `epsTTM`, `roiTTM`, `revenueTTM`
- **Anual**: `peAnnual`, `epsAnnual`, `roeRfy`, `bookValuePerShareAnnual`
- **Trimestral**: `bookValuePerShareQuarterly`, `currentRatioQuarterly`, `pbQuarterly`
- **5 años**: `epsGrowth5Y`, `revenueGrowth5Y`, `roi5Y`, `ebitdaCagr5Y`
- **3 años**: `epsGrowth3Y`, `revenueGrowth3Y`

> ⚠️ **Importante:** `metric` no tiene historia. Es solo el último valor disponible. Para series temporales históricas usar `stock/earnings` (4 quarters free) o `stock/financials` (premium, años de data).

---

### GET /stock/earnings — Historial de Earnings ✅ FREE

**Confirmado funcionando.** En plan gratuito devuelve **exactamente 4 quarters** (sin importar el parámetro `limit`). Premium tiene más historia.

| Parámetro | Requerido |
|-----------|-----------|
| `symbol` | ✅ |
| `limit` | ❌ (default: 5, pero free lo limita a 4) |

**Respuesta típica (free):**
```
2026-03-31 | epsActual: N/A | surprise: 1.08%
2025-12-31 | epsActual: N/A | surprise: 4.19%
2025-09-30 | epsActual: N/A | surprise: 2.35%
2025-06-30 | epsActual: N/A | surprise: 7.34%
```

---

### GET /stock/recommendation — Recomendaciones de Analistas ✅ FREE

**Confirmado funcionando.** Devuelve datos mensuales desde aproximadamente 8 meses atrás.

| Parámetro | Requerido |
|-----------|-----------|
| `symbol` | ✅ |

**Respuesta típica:**
```
2026-06-01: SB=14 B=24 H=15 S=2 SS=0
2026-05-01: SB=15 B=24 H=13 S=2 SS=0
2026-04-01: SB=14 B=23 H=15 S=2 SS=0
2026-03-01: SB=14 B=22 H=16 S=2 SS=0
...
```

### GET /stock/financials — Estados Financieros 🔒 PREMIUM

Income statement, balance sheet, cash flow. **Requiere plan pago.**

---

### GET /stock/financials-reported — SEC Financials 🔒 PREMIUM

---

### GET /stock/price-target — Price Targets 🔒 PREMIUM

Devuelve 403 con API key gratuita.

---

### GET /stock/earnings-calendar — Calendario de Earnings 🔒 PREMIUM

---

### GET /stock/dividend — Historial de Dividendos 🔒 PREMIUM

Devuelve 403 con API key gratuita.

---

### GET /stock/split — Historial de Splits 🔒 PREMIUM

---

### GET /calendar/ipo — Calendario de IPO 🔒 PREMIUM

---

### Endpoints Fundamentales Adicionales 🔒 PREMIUM

| Endpoint | Descripción |
|----------|-------------|
| `GET /stock/insider-transactions` | Transacciones de insider |
| `GET /stock/insider-sentiment` | Sentimiento de insiders |
| `GET /stock/revenue-estimate` | Estimaciones de ingresos |
| `GET /stock/eps-estimate` | Estimaciones de EPS |
| `GET /stock/ebitda-estimate` | Estimaciones de EBITDA |
| `GET /stock/ownership` | Lista completa de accionistas |
| `GET /stock/executive` | Ejecutivos con compensación |
| `GET /stock/profile` | Perfil empresa v1 (descripción completa) |

---

## 3. Noticias y Sentimiento

### GET /company-news — Noticias por Empresa ✅ FREE

1 año de historia en free, 20 años en premium. **Confirmado funcionando.**

| Parámetro | Requerido |
|-----------|-----------|
| `symbol` | ✅ |
| `from` | ✅ (YYYY-MM-DD) |
| `to` | ✅ (YYYY-MM-DD) |

---

### GET /news — Noticias del Mercado ✅ FREE

**Confirmado funcionando.**

| Parámetro | Requerido |
|-----------|-----------|
| `category` | ✅ (`general`, `forex`, `crypto`, `merger`) |

---

### GET /news-sentiment / /press-releases 🔒 PREMIUM

---

## 4. Forex 🔒 PREMIUM

> ⚠️ Todos los endpoints de Forex requieren plan pago (forex/rates devuelve 403 con key gratuita).

| Endpoint | Descripción |
|----------|-------------|
| `GET /forex/rates` | Tasas de cambio |
| `GET /forex/candle` | Velas forex |
| `GET /forex/exchange` | Brokers forex |
| `GET /forex/symbol` | Pares forex |

---

## 5. Criptomonedas 🔒 PREMIUM

> ⚠️ Todos los endpoints de Crypto requieren plan pago (crypto/candle devuelve 403 con key gratuita).

| Endpoint | Descripción |
|----------|-------------|
| `GET /crypto/candle` | Velas crypto |
| `GET /crypto/exchange` | Exchanges crypto |
| `GET /crypto/symbol` | Símbolos crypto |

---

## 6. Datos Económicos 🔒 PREMIUM

> ⚠️ Todos los endpoints de datos económicos requieren plan pago.

| Endpoint | Descripción |
|----------|-------------|
| `GET /economic/code` | Códigos de indicadores |
| `GET /economic` | Datos históricos |
| `GET /country` | Metadatos de países |
| `GET /calendar/economic` | Calendario económico |

---

## 7. ETFs, Índices, Bonos 🔒 PREMIUM

| Endpoint | Descripción |
|----------|-------------|
| `GET /etf/profile` | Perfil ETF |
| `GET /etf/holdings` | Holdings ETF |
| `GET /index/constituents` | Constituyentes índice |
| `GET /bond/profile` | Perfil de bono |
| `GET /bond/price` | Precio de bono |

---

## 8. Datos Alternativos 🔒 PREMIUM

| Endpoint | Descripción |
|----------|-------------|
| `GET /social-sentiment` | Sentimiento redes sociales |
| `GET /covid-19` | Datos COVID-19 |
| `GET /senate-lobbying` | Lobbying Senado |
| `GET /esg-score` | Scores ESG |
| `GET /supply-chain` | Cadena de suministro |
| `GET /investment-themes` | Temas de inversión |

---

## 9. Mutual Funds 🔒 PREMIUM

| Endpoint | Descripción |
|----------|-------------|
| `GET /mutual-fund/profile` | Perfil de fondo |
| `GET /mutual-fund/holdings` | Holdings de fondo |

---

## 10. Búsqueda y Referencia

### GET /search — Búsqueda de Símbolos ✅ FREE

**Confirmado funcionando.**

| Parámetro | Requerido |
|-----------|-----------|
| `q` | ✅ |
| `exchange` | ❌ |

---

## 11. WebSocket

### WebSocket Trades — Streaming de Trades en Vivo ✅ FREE (no test)

Plan gratuito: **50 símbolos**. Premium: ilimitado.

**URL:** `wss://ws.finnhub.io?token=API_KEY`

### WebSocket News 🔒 PREMIUM

### WebSocket Press Releases 🔒 ENTERPRISE

---

## Resumen: Endpoints ✅ FREE (confirmados en plan gratuito)

| # | Endpoint | Descripción |
|---|----------|-------------|
| 1 | `GET /quote` | Cotización en tiempo real |
| 2 | `GET /stock/profile2` | Perfil de empresa v2 |
| 3 | `GET /stock/peers` | Empresas similares |
| 4 | `GET /stock/earnings` | Earnings históricos |
| 5 | `GET /stock/recommendation` | Recomendaciones de analistas |
| 6 | `GET /stock/metric` | Métricas financieras clave |
| 7 | `GET /company-news` | Noticias por empresa |
| 8 | `GET /news` | Noticias del mercado |
| 9 | `GET /search` | Búsqueda de símbolos |
| 10 | `GET /stock/market-status` | Estado del mercado |

> **Solo estos 10 endpoints funcionan en el plan gratuito.** El resto requiere plan pago.

---

## Resumen: Endpoints 🔒 PREMIUM (requieren plan pago)

| Endpoint | Descripción |
|----------|-------------|
| `GET /stock/candle` | Velas OHLCV históricas |
| `GET /stock/financials` | Estados financieros |
| `GET /stock/financials-reported` | SEC Financials |
| `GET /stock/price-target` | Price targets |
| `GET /stock/dividend` | Dividendos históricos |
| `GET /stock/split` | Splits históricos |
| `GET /stock/earnings-calendar` | Calendario de earnings |
| `GET /calendar/ipo` | Calendario IPO |
| `GET /stock/symbol` | Listado de símbolos |
| `GET /stock/market-holiday` | Feriados del mercado |
| `GET /forex/rates` | Tasas de cambio |
| `GET /forex/candle` | Velas forex |
| `GET /forex/exchange` | Brokers forex |
| `GET /forex/symbol` | Pares forex |
| `GET /crypto/candle` | Velas crypto |
| `GET /crypto/exchange` | Exchanges crypto |
| `GET /crypto/symbol` | Símbolos crypto |
| `GET /economic/code` | Códigos económicos |
| `GET /economic` | Datos económicos |
| `GET /country` | Metadatos de países |
| `WebSocket Trades` | Streaming trades (50+ símbolos) |
| `GET /stock/profile` | Perfil empresa v1 completo |
| `GET /stock/insider-transactions` | Transacciones insider |
| `GET /stock/insider-sentiment` | Sentimiento insider |
| `GET /stock/ownership` | Accionistas completo |
| `GET /stock/executive` | Ejecutivos + compensación |
| `GET /news-sentiment` | Sentimiento noticias |
| `GET /press-releases` | Press releases |
| `GET /etf/profile` | Perfil ETF |
| `GET /etf/holdings` | Holdings ETF |
| `GET /index/constituents` | Constituyentes índice |
| `GET /social-sentiment` | Sentimiento redes |
| `GET /esg-score` | ESG scores |
| `GET /calendar/economic` | Calendario económico |
| Todos los de bonos y mutual funds | Datos de bonos y fondos |
| Todos los alternativos | ESG, patentes, lobbying, etc. |

---

## Códigos de Error

| Código | Significado | Solución |
|--------|-------------|----------|
| 200 | OK | — |
| 401 | No autorizado | API key inválida o faltante |
| 403 | Prohibido | Endpoint premium sin plan pago |
| 404 | No encontrado | Símbolo o recurso inexistente |
| 429 | Too Many Requests | Excediste rate limit (60/min free, 30/s global) |
| 500 | Error interno | Error del servidor Finnhub |

### Cómo detectar endpoint premium bloqueado

Si intentás un endpoint premium con key gratuita, recibís:

```json
{
  "error": "You don't have access to this resource."
}
```
