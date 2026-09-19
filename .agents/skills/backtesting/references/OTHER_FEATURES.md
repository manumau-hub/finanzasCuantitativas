# Otras Features: Fundamental, Sentimiento, Exógenos

## A — Análisis Fundamental (Clase 8)

Funciones en `scripts/fundamental_ratios.py`:

- **Income metrics**: gross margin, operating margin, net margin, EBITDA margin
- **Balance metrics**: D/E, debt/assets, current/quick/cash ratios
- **Cash flow metrics**: FCF, CFO/revenue, CFO/net income
- **Valuación**: P/E, P/B, P/S, EV/EBITDA
- **Rentabilidad**: ROE, ROA, ROIC
- **DuPont**: descomposición del ROE en 5 componentes (tax burden × interest
  burden × margin × turnover × leverage)
- **Altman Z-Score**: predicción de quiebra (Z > 2.99 = safe, 1.81-2.99 =
  grey zone, < 1.81 = distress)
- **Piotroski F-Score**: 9 criterios binarios de calidad fundamental
  (0 = débil, 9 = fuerte)

### Fuentes de datos

Skills del repositorio que proveen datos financieros estructurados:

| Dato | Skills Fuente |
|------|---------------|
| Income Statement | sec-data, macrotrends, barchart, yahoo-finance, marketwatch, google-finance |
| Balance Sheet | sec-data, macrotrends, barchart, yahoo-finance, marketwatch, google-finance |
| Cash Flow | sec-data, macrotrends, barchart, yahoo-finance, marketwatch, google-finance |
| Valuation Ratios | finviz, barchart, simplywallst, morningstar, companiesmarketcap |
| Institutional Holdings | nasdaq-data (13F), marketscreener |
| Insider Trading | nasdaq-data, barchart, finviz, marketscreener |
| Earnings Transcripts | earningswhispers |
| Analyst Ratings | barchart, google-finance, marketwatch, finnhub, marketscreener |
| Fundamental Screener | morningstar (102K+ listings), tradingview |

---

## B — Sentimiento (Clase 9)

No hay implementación de código en este skill. Los recursos abajo son puntos
de partida para implementación propia.

### Papers

- **Loughran-McDonald (2011)**: diccionario financiero para NLP. Master
  dictionary con 6 sentimientos (positive, negative, uncertainty, litigious,
  constraining, superfluous). Mejor que diccionarios genéricos (AFINN, LIWC).
- **Tetlock (2007)**: contenido de medios → presión en precios de acciones.
- **Bollen-Mao-Zeng (2011)**: Twitter sentiment predice el Dow Jones.
- **Hutto-Gilbert (2014)**: VADER — rule-based sentiment para redes sociales.
  Bueno para detectar sarcasmo y énfasis.

### Fuentes de datos

- **News**: finnhub (noticias por ticker), tradingview (headlines ~200/stock),
  google-finance (news con thumbnails), earningswhispers (transcripciones
  completas de earnings calls).
- **Social media**: APIs de Reddit, X/Twitter, StockTwits.
- **Alternative data**: Google Trends, SEC filings language, job postings
  (LinkedIn, Indeed).

### Edge

El sentimiento es la única clase que captura **narrativa** — el relato que
justifica los movimientos de precio. Un análisis técnico impecable no puede
anticipar un cambio repentino en el sentimiento del mercado (un pánico, un
FOMO, una noticia sorpresa). Combinando sentimiento + precio se pueden
detectar divergencias: si el precio sube pero el sentimiento se deteriora,
es una señal de debilidad que ningún otro indicador captura.

---

## C — Exógenos (Clase 10)

Tampoco hay implementación de código. Recursos para implementación propia.

### Categorías

| Categoría | Ejemplos | Fuentes |
|-----------|----------|---------|
| Tasas | Fed Funds, T10Y, T2Y, SOFR, BADLAR | FRED, BCRA, investing |
| Inflación | CPI, PCE, IPC, CER | FRED, INDEC |
| Actividad | GDP, PMI, EMAE, empleo | FRED, INDEC |
| Volatilidad | VIX, VDAX, MERVAL vol | CBOE, yahoo-finance |
| Liquidez | M2, reservas bancarias, base monetaria | FRED, BCRA |
| Commodities | Oil, gold, copper, grains | investing, yahoo-finance |
| FX | DXY, EURUSD, USDARS | FRED, BCRA, investing |
| On-chain (crypto) | BTC hash rate, active addresses, exchange flows | Glassnode, CoinMetrics |

### Edge

Los exógenos capturan el **régimen macro** — el estado del ciclo económico
que determina qué clases de activos y qué estrategias funcionan. Un
trend-following en bonos funciona bien en mercados con tendencia de tasas
clara, pero da señales opuestas cuando el régimen cambia. Incorporar exógenos
permite rotar entre estrategias según el régimen en lugar de operar siempre
la misma. Ejemplos:

- Si VIX > 30 y subiendo: reducir tamaño de posición, priorizar activos
  defensivos (gold, treasuries).
- Si la pendiente de la curva (T10Y-T2Y) se invierte: probable recesión →
  rotar de value a growth o de equities a bonds.
- Si el CPI está acelerando: posicionarse en inflation hedges (commodities,
  TIPS, real estate).
- Si la base monetaria se contrae: reducir riesgo sistemático.

### Referencias

- **FRED Macro skill**: 840K+ series macro de la Fed (tasas, empleo, GDP,
  money supply, etc).
- **BCRA Macro skill**: series macro argentinas del BCRA (reservas, tasas,
  CER, UVA, base monetaria).
- **INDEC skill**: series oficiales argentinas (~4250 series: IPC, EMAE,
  empleo, pobreza, salarios).
- **CBOE skill**: VIX, índices de volatilidad, VX futures.
- **TradingView screener**: screener masivo con columnas macro (interest rate,
  inflation) en ciertos mercados.
