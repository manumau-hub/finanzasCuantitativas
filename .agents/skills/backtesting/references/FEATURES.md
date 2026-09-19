# Indicadores y Features — Taxonomía de 10 Clases

Implementados en `scripts/indicators.py`. Cada clase cubre una dimensión
distinta de la información de mercado, con propiedades matemáticas,
parámetros y casos de uso específicos.

---

## Clase 1a: Trend-Following (precio)

**Qué son:** Filtros paso-bajo sobre la serie de precios. Suprimen el ruido
de alta frecuencia para revelar la dirección subyacente. Operan con rezago
(phase lag) intrínseco: a mayor suavizado, mayor rezago.

### Matemática

| Indicador | Fórmula | Parámetros |
|-----------|---------|------------|
| SMA | (1/n) Σᵢ₌₀ⁿ⁻¹ Pₜ₋ᵢ | n = ventana |
| EMA | α·Pₜ + (1-α)·EMAₜ₋₁, α = 2/(n+1) | n = período de decaimiento |
| WMA | Σᵢ₌₁ⁿ wᵢ·Pₜ₋ᵢ₊₁, wᵢ = 2i/(n(n+1)) | n = ventana, pesos lineales |
| DEMA | 2·EMAₙ(P) − EMAₙ(EMAₙ(P)) | n, elimina ~50% del lag |
| TEMA | 3·EMA₁ − 3·EMA₂ + EMA₃ (notación: EMAₖ = EMAⁿ aplicada k veces) | n, elimina ~67% del lag |
| TRIMA | SMA(SMA(P, n), n) centrada | n, suavizado doble |

**Lag teórico:** SMA(n) tiene lag = (n-1)/2. EMA(n) tiene lag ≈ (n-1)/2
también en estado estacionario, pero responde más rápido a cambios recientes.
DEMA reduce el lag ~50%, TEMA ~67%, pero amplifican ruido.

### Edge entre variantes

- **SMA**: usada para señales discretas (cruces) porque sus discontinuidades
  son más limpias. Ej: SMA 50/200 crossover.
- **EMA**: mejor para sistemas continuos (weight, z-score) porque da más peso
  a datos recientes. Más sensible a cambios de régimen.
- **DEMA/TEMA**: útiles cuando se necesita respuesta rápida pero no se quiere
  usar ventanas cortas (que amplifican ruido). Compromiso: menos lag pero más
  sensibilidad a outliers.
- **TRIMA**: suavizado extremo, elimina casi todo el ruido pero con mucho lag.
  Útil para filtros de muy largo plazo (> 1 año).

### MACD

```
MACD = EMA₁₂(P) − EMA₂₆(P)
Signal = EMA₉(MACD)
Histogram = MACD − Signal
```

Construcción: diferencia de dos EMAs (rápida − lenta) crea un oscilador que
elimina la tendencia de largo plazo. La Signal es un filtro adicional. El
cruce de MACD y Signal da señales de momentum. La divergencia entre MACD y
precio es una de las señales más estudiadas (aunque con baja relación
señal/ruido en términos prácticos).

### ADX

```
+DM = Hₜ − Hₜ₋₁ (si > Lₜ₋₁ − Lₜ y > 0, sino 0)
−DM = Lₜ₋₁ − Lₜ (si > Hₜ − Hₜ₋₁ y > 0, sino 0)
TR = max(Hₜ−Lₜ, |Hₜ−Cₜ₋₁|, |Lₜ−Cₜ₋₁|)
+DI = EMAₙ(+DM) / EMAₙ(TR)
−DI = EMAₙ(−DM) / EMAₙ(TR)
DX = |+DI − −DI| / (+DI + −DI)
ADX = EMAₙ(DX)
```

ADX mide la fuerza de la tendencia (no la dirección). Valores > 25 indican
tendencia. +DI/−DI dan la dirección. La combinación ADX > 25 Y +DI > −DI
es una de las configuraciones más robustas para trend-following.

### Indicadores incluidos

SMA, EMA, WMA, DEMA, TRIMA, TEMA, MACD, ADX, DX, ADXR, +DI/-DI, +DM/-DM,
SAR, MOM, MIDPOINT, MIDPRICE.

---

## Clase 1b: Osciladores (precio)

**Qué son:** Transformaciones de precio acotadas a un rango fijo (típicamente
0-100 o -1 a 1). Miden la velocidad del cambio de precio (momentum) o la
posición relativa dentro de un rango histórico.

### RSI (Relative Strength Index)

```
RSI = 100 − 100 / (1 + RS)
RS = EMAₙ(ΔP⁺) / EMAₙ(|ΔP⁻|)
```

Donde ΔP⁺ = max(Pₜ−Pₜ₋₁, 0), ΔP⁻ = min(Pₜ−Pₜ₋₁, 0). Wilder original usa
SMA en vez de EMA. Fórmula con EMA converge más rápido a valores estables.

RSI mide la magnitud de las ganancias recientes vs las pérdidas recientes,
normalizado a [0, 100]. Niveles clásicos: 30/70 (sobreventa/sobrecompra).

**Edge vs precio puro:** RSI puede mostrar **divergencia** — el precio hace
un nuevo máximo pero RSI no (divergencia bajista). Esto es señal de
debilidad subyacente que el precio no muestra. Sin embargo, la divergencia
tiene baja tasa de acierto como señal independiente; funciona mejor como
filtro (no tomar señales trend-following si hay divergencia).

### Stochastics (%K, %D)

```
%K = 100 × (Cₜ − Lₙ) / (Hₙ − Lₙ)
%D = SMA₃(%K)
```

Donde Lₙ, Hₙ son mínimos/máximos de n períodos. %K mide dónde cerró el precio
dentro del rango reciente. %D es una media suavizada.

**Diferencia con RSI:** Stochastics usa el rango de precio (high-low), no el
cambio día a día. Es más volátil que RSI y da más señales. Slow stochastics
(%D) es la versión más usada.

### MFI (Money Flow Index)

```
MFI = 100 − 100 / (1 + MFR)
MFR = Σ MF⁺ / Σ MF⁻
MF = Typical Price × Volume
```

Como RSI pero ponderado por volumen. Añade la dimensión de flujo. MFI > 80
con precio subiendo pero MFI bajando = distribución (divergencia más confiable
que RSI porque incorpora volumen).

### Indicadores incluidos

WILLR, APO, PPO, STOCH, STOCHF, RSI, BOP, CMO, ROC, MFI, TRIX, ULTOSC.

---

## Clase 1c: Contrarios (saturación)

**Qué son:** Detectan cuándo el precio está en un extremo estadístico de su
distribución reciente, sugiriendo agotamiento de la tendencia o reversión
inminente. Operan más rápido que trend-following en puntos de inflexión.

### Bollinger Bands

```
Middle = SMAₙ(P)
Upper = SMAₙ(P) + k · σₙ(P)
Lower = SMAₙ(P) − k · σₙ(P)
```

Bandas de volatilidad: cuando el precio toca la banda superior, está a k
desviaciones estándar de la media de n días. n=20, k=2 es el default de
Bollinger original.

**Edge cuantitativo:** Las bandas son dinámicas — se ensanchan en alta
volatilidad y se contraen en baja vol. Un contracción extrema (squeeze)
suele preceder a movimientos grandes. El ancho de banda normalizado
(Width = (Upper−Lower)/Middle) es un predictor de vol futura.

**Contrarian:** Comprar en banda inferior y vender en banda superior funciona
en rangos laterales. En tendencias fuertes, el precio puede "caminar" la
banda — en ese caso el indicador deja de ser contrario y el trend-following
(Clase 1a) es más apropiado.

### CCI (Commodity Channel Index)

```
CCI = (TPₜ − SMAₙ(TP)) / (0.015 · MDₙ)
TP = (H + L + C) / 3
MDₙ = desviación media absoluta de TP en n períodos
```

Similar a Bollinger pero usa Typical Price en vez de close y desviación media
absoluta en vez de std. Más sensible a outliers.

### ATR (Average True Range)

```
TR = max(Hₜ−Lₜ, |Hₜ−Cₜ₋₁|, |Lₜ−Cₜ₋₁|)
ATR = EMAₙ(TR)
```

No es un oscilador ni da dirección — es un **estimador de volatilidad**.
Se usa para:
- Tamaño de posición (invertir menos cuando ATR es alto)
- Stop loss dinámico (stops a múltiplo de ATR)
- Normalizar indicadores entre activos de distinta volatilidad

### Indicadores incluidos

CCI, AROON, AROONOSC, BBANDS, TRANGE, ATR.

---

## Clase 2: Flujo (volumen, derivados)

**Qué son:** Incorporan información de volumen, open interest y flujo de
órdenes. Operan en una dimensión ortogonal al precio — precio y volumen son
semindependientes.

### OBV (On-Balance Volume)

```
OBVₜ = OBVₜ₋₁ + Volₜ si Cₜ > Cₜ₋₁
OBVₜ = OBVₜ₋₁ − Volₜ si Cₜ < Cₜ₋₁
OBVₜ = OBVₜ₋₁ si Cₜ = Cₜ₋₁
```

Acumula volumen en dirección del cambio de precio. Es un indicador de flujo
neto. La divergencia OBV-precio es una de las señales más antiguas y
respetadas: el precio sube pero OBV baja = distribución (smart money vendiendo).

**Limitación:** OBV ignora la magnitud del cambio de precio — todo movimiento
alcista pesa igual, sea +0.01% o +5%. AD (Acumulación/Distribuición) corrige
esto ponderando por dónde cerró el precio dentro del rango del día.

### AD (Acumulación/Distribución)

```
MFM = ((Cₜ − Lₜ) − (Hₜ − Cₜ)) / (Hₜ − Lₜ)  (Money Flow Multiplier)
ADₜ = ADₜ₋₁ + MFM × Volₜ
```

MFM va de -1 a +1 ponderando la posición del cierre en el rango del día.
AD es más preciso que OBV porque captura la intesidad del movimiento.

### VWAP

```
VWAPₜ = Σ(Pᵢ · Volᵢ) / Σ(Volᵢ), i = 1..t dentro del día
```

Usado por institucionales como benchmark de ejecución. Precio por encima de
VWAP = sesgo comprador, por debajo = sesgo vendedor.

### Indicadores incluidos

VWAP, OBV, AD, ADOSC. Interfaces para métricas externas (put/call ratio,
funding rate, open interest change).

---

## Clase 3: Combinados y Normalización

**Qué son:** Operadores sobre indicadores — los combinan, normalizan y
transforman para construir señales multi-dimensionales.

### cross_indicator(A, B, method='zscore_weight')

Pondera el indicador A por el z-score de B. Matemáticamente:

```
zB = (Bₜ − rolling_mean(B, n)) / rolling_std(B, n)
output = A × Φ(zB)
```

Donde Φ es la CDF normal (comprime z-scores extremos a [0,1]). Funciona
como una compuerta: B confirma o refuta la señal de A. Ejemplo: RSI
confirmado por volumen (OBV z-score alto).

### range_bound(series, window)

```
output = (series − rolling_min(series, n)) / (rolling_max(series, n) − rolling_min(series, n))
```

Mapea cualquier serie a [0, 1] usando min/max rolling. Útil para normalizar
indicadores heterogéneos (ej: RSI [0,100] + CCI [-∞,∞] + MFI [0,100]) antes
de combinarlos. El rolling window evita look-ahead bias.

### zscore_norm(series, window)

```
output = (series − rolling_mean(series, n)) / rolling_std(series, n)
```

Normalización gaussiana rolling. Output es adimensional — permite sumar
señales de diferentes indicadores sin que uno domine por escala.

**⚠️ CRÍTICO:** Todas las normalizaciones deben usar ventanas **rolling**.
Estadísticas globales introducen **look-ahead bias** (data leak).

---

## Clase 4: Conteos Discretos (Poisson, Binomial)

**Qué son:** Modelos probabilísticos para eventos discretos — no para series
temporales continuas. Miden frecuencia de ocurrencia, no magnitud.

### Poisson Rate

```
λ̂ = N_eventos / T_períodos
P(k eventos en t) = e^{−λt} · (λt)ᵏ / k!
```

Para eventos raros: flash crashes, defaults, gaps de precio, saltos de
volatilidad. El λ estimado permite calcular probabilidad de que ocurran 0, 1,
o N eventos en un período futuro.

**Edge:** Un activo puede tener baja volatilidad (medidas continuas normales)
pero alta tasa de eventos extremos (Poisson). Esto es invisible para todas
las clases anteriores.

### Binomial Ratio

```
p̂ = N_éxitos / N_intentos
```

Proporción de días positivos sobre total. Con corrección para muestras
pequeñas (unbiased_estimator). Útil para medir consistencia de una estrategia
independientemente de la magnitud de las ganancias.

### Indicadores incluidos

`poisson_rate(events, period)`, `binomial_ratio(successes, trials)`,
`unbiased_estimator(p_hat, n)`, `event_probability(rate, threshold)`.

---

## Clase 5: Estacionalidad

**Qué son:** Patrones periódicos determinísticos — no dependen del precio
sino del momento temporal (hora, día, mes, ciclo).

### Fourier Terms

```
ϕⱼ(t) = sin(2πjt / T), cos(2πjt / T), j = 1..n
```

Genera n pares sin/cos para cualquier período T. Son features ortogonales
que capturan ciclos de cualquier frecuencia sin ventanas móviles ni rezago.
Se usan como entrada para modelos ML (regresión lineal, random forest, etc.).
La ventaja sobre seasonal_profile: no requieren datos históricos del activo
— son determinísticos.

### STL Decomposition

Descompone la serie en tendencia + estacionalidad + residuo usando
LOESS (regresión local). Wrapper de `statsmodels.tsa.seasonal.STL`.
Parámetros: periodo (días), seasonal (longitud del smoother sazonal),
trend (longitud del smoother de tendencia).

### seasonal_profile

```
promedio(serie[índices_del_mismo_período])
```

Agrupa observaciones por período (lunes, martes, ..., hora 1, hora 2, ...)
y calcula el promedio. Simple y efectivo para detectar patrones de calendario.

### Edge

Los trend-following detectan tendencia **después** de que aparece. La
estacionalidad predice movimientos **antes** de que ocurran, basándose en
patrones temporales repetitivos. El edge combinado: usar estacionalidad para
sesgar posición (ej: tender a estar largo en enero por January effect) y
trend-following para confirmar la entrada.

### Indicadores incluidos

`seasonal_profile(series, period)`, `fourier_terms(T, n_terms)`,
`stl_decompose(series, period)`.

---

## Clase 6: Estadísticos

**Qué son:** Momentos móviles de la distribución de retornos. Miden forma,
no dirección.

### Momentos Rolling

```
μₜ = rolling_mean(r, n)
σₜ = rolling_std(r, n)
γₜ = rolling_skew(r, n)    — asimetría: positiva = cola derecha larga
κₜ = rolling_kurt(r, n)    — curtosis: > 3 = colas más pesadas que normal
```

La ventana n debe ser lo suficientemente grande para estimación estable
(mínimo 21 días para skew/kurt, 63+ recomendado). Valores individuales son
ruidosos; analizar la evolución (tendencia de skew/kurt) más que el valor
absoluto.

### Tails Ratio

```
TR(α) = Q(1−α) / Q(α)
```

Ratio de quantiles superior a inferiores. Mide simetría de colas. TR > 2
indica asimetría significativa. Complementa a skewness pero es más robusto
a outliers extremos.

### Best Fit Distribution

Para 5 distribuciones paramétricas: Normal (2 params), t (3), NCt (4),
Laplace (2), Johnson SU (4). Johnson SU:

```
Z = γ + δ · sinh⁻¹((X − ξ) / λ)
X = ξ + λ · sinh((Z − γ) / δ)
```

Johnson SU captura asimetría y curtosis arbitrarias. Es la única distribución
con 4 parámetros que puede modelar cualquier combinación de skew/kurt.
En la práctica, es el mejor fit para retornos de equities (ver VALIDATION.md,
Level 1 — marginal test: KS ≈ 0.01 vs Normal ≈ 0.07).

### Indicadores incluidos

`rolling_vol(returns, window)`, `rolling_skew(returns, window)`,
`rolling_kurt(returns, window)`, `tails_ratio(returns, alpha)`,
`zscore(series, window=None)`, `best_fit_dist(returns)`,
`fit_distribution(returns, name)`.

---

## Clase 7: Referenciales (benchmark)

**Qué son:** Métricas relativas entre pares de activos. Miden relaciones,
no valores absolutos.

### Beta y Alpha

```
β = Cov(r_strat, r_bench) / Var(r_bench)
α = (r_strat − r_f) − β · (r_bench − r_f)
```

Beta mide exposición sistemática al benchmark. Beta = 1: el activo se mueve
con el mercado. Beta = 0: no hay correlación. Beta < 0: inverso.

Alpha de Jensen: retorno ajustado por riesgo de mercado. Es el estándar para
evaluar si un manager agrega valor vs una estrategia pasiva. α > 0 significa
que la estrategia superó al benchmark ajustado por riesgo.

### Rolling Correlation

```
ρₜ(A, B) = rolling_cov(A, B, n) / (rolling_std(A, n) · rolling_std(B, n))
```

Soporta Pearson, Kendall y Spearman. Pearson captura correlación lineal;
Spearman captura cualquier relación monótona (mejor para activos con
relaciones no lineales). Kendall es más robusto a outliers.

### Cross-Asset Matrix

Genera la matriz de correlación completa para N activos. Útil para:
- Detectar cambios de régimen (todas las correlaciones tienden a 1 en crisis).
- Identificar activos con baja correlación (candidatos a diversificación).
- Construir portfolios con correlación objetivo.

### Cross-Timeframe Correlation

Correlación entre la misma serie a diferentes frecuencias (ej: retornos
diarios vs semanales). Si la correlación intra-timeframe es baja, la señal
no es consistente en temporalidades — posible overfitting.

### Indicadores incluidos

`alpha(strat, bench, rf)`, `beta(strat, bench)`,
`rolling_corr(A, B, window, method)`, `cross_asset_matrix(returns_df, method)`,
`cross_timeframe_corr(A, B, periods)`.

---

## Clase 8: Fundamentales

Implementados en `scripts/fundamental_ratios.py`.

### Altman Z-Score (predicción de quiebra)

```
Z = 1.2·A + 1.4·B + 3.3·C + 0.6·D + 1.0·E

A = Working Capital / Total Assets    — liquidez operativa
B = Retained Earnings / Total Assets   — rentabilidad acumulada
C = EBIT / Total Assets                — productividad de activos
D = Market Cap / Total Liabilities     — solvencia de mercado
E = Sales / Total Assets               — rotación de activos
```

Z > 2.99: seguro. 1.81 < Z < 2.99: zona gris. Z < 1.81: distress.

**No aplicar a bancos o financials:** el working capital negativo es
estructural en bancos (prestan dinero a largo, toman depósitos a corto).
El Z-score de un banco sano puede ser < 1.81, dando falsos positivos.

### Piotroski F-Score (calidad fundamental)

9 criterios binarios (0/1), puntaje 0-9:

**Rentabilidad (4):** NI > 0, CFO > 0, ROA mejoró, CFO > NI.
**Leverage/Liquidez (3):** deuda/activos bajó, current ratio mejoró,
  acciones no diluidas.
**Eficiencia operativa (2):** margen bruto mejoró, rotación de activos mejoró.

F-Score ≥ 7: fundamentalmente fuerte. ≤ 3: débil. Útil como filtro de
selección de acciones: comprar solo empresas con F-Score ≥ 7.

### DuPont (descomposición ROE)

```
ROE = NI / Equity = Tax × Interest × Margin × Turnover × Leverage
     = (NI/EBT) × (EBT/EBIT) × (EBIT/Rev) × (Rev/Assets) × (Assets/Equity)
```

Descompone el ROE en 5 factores que identifican la fuente del retorno:
- **Tax burden**: cuánto retiene la empresa después de impuestos.
- **Interest burden**: cuánto retiene después de intereses.
- **Operating margin**: rentabilidad operativa (core business).
- **Asset turnover**: eficiencia en uso de activos.
- **Leverage**: apalancamiento financiero.

Dos empresas con el mismo ROE pueden tener perfiles de riesgo muy distintos
(ej: una con alto margin y bajo leverage, otra con bajo margin y alto
leverage).

### Fuentes de datos

Acepta DataFrames de: sec-data, marketwatch, investing, macrotrends,
barchart, yahoo-finance, nasdaq-data, simplywallst, finviz.

---

## Clase 9: Sentimiento

Sin implementación de código en este skill. Recursos en
`references/OTHER_FEATURES.md`.

**Papers clave:** Loughran-McDonald (2011) — diccionario financiero NLP.
Tetlock (2007) — contenido de medios → precio. VADER (Hutto-Gilbert, 2014)
— rule-based sentiment para redes sociales.

**Edge:** El sentimiento captura **narrativa** — ortogonal al precio y
fundamentales. Permite detectar divergencias precio-sentimiento que ningún
otro indicador captura.

---

## Clase 10: Exógenos

Sin implementación de código. Recursos en `references/OTHER_FEATURES.md`.

**Categorías:** tasas (Fed Funds, T10Y), inflación (CPI, IPC), actividad
(GDP, PMI), volatilidad (VIX), liquidez (M2), commodities, FX, on-chain.

**Edge:** Capturan el **régimen macro** que determina qué estrategias
funcionan. Permiten rotar entre estrategias según el contexto económico,
no operar siempre la misma.

---

## Resumen de Edges por Clase

| Clase | Dimensión | Edge técnico |
|-------|-----------|--------------|
| 1a Trend | Dirección (filtro paso-bajo) | Más robusto en tendencias, fase lag conocida |
| 1b Osciladores | Momentum (derivada) | Divergencias anticipan cambios (baja SNR, requiere filtro) |
| 1c Contrarios | Saturación (colas de distribución) | Timing de reversión en rangos laterales |
| 2 Flujo | Convicción (volumen) | Divergencias más confiables (smart money detection) |
| 3 Combinados | Confluencia (normalización) | Elimina look-ahead bias vía rolling windows |
| 4 Conteos | Frecuencia (Poisson/Binomial) | Ortogonal a mediciones continuas |
| 5 Estacionalidad | Ciclos (Fourier/STL) | Features determinísticos sin rezago |
| 6 Estadísticos | Forma de distribución | Detecta cambios de régimen de riesgo pre-crash |
| 7 Referenciales | Relaciones (correlación) | Detecta cambios de régimen en correlaciones |
| 8 Fundamentales | Salud contable (ratios) | Ortogonal al precio, filtro de selección |
| 9 Sentimiento | Narrativa (NLP) | Detecta divergencias precio-relato |
| 10 Exógenos | Contexto macro | Rotación de estrategias por régimen |
