# Theory — Por que cada metodo, cuando usar, cuando NO

Para la guia practica de uso, ver `SKILL.md`. La teoria matematica
detallada de cada modelo esta en `REFERENCE.md`. Este documento se enfoca
exclusivamente en **cuando** y **por que** usar cada uno, con tablas
comparativas.

---

## Indice

1. [Criterios de decision rapida](#1-criterios-de-decision-rapida)
2. [Tabla maestra: precision, velocidad, supuestos](#2-tabla-maestra)
3. [Por que de cada metodo](#3-por-que-de-cada-metodo)
   - [3.1 Black-Scholes](#31-black-scholes)
   - [3.2 Bjerksund-Stensland 2002 / BAW](#32-bjerksund-stensland-2002--baw)
   - [3.3 Binomial CRR](#33-binomial-crr)
   - [3.4 Trinomial Boyle](#34-trinomial-boyle)
   - [3.5 Monte Carlo antithetic](#35-monte-carlo-antithetic)
   - [3.6 Longstaff-Schwartz](#36-longstaff-schwartz)
   - [3.7 Heston 1993](#37-heston-1993)
   - [3.8 Bates 1996](#38-bates-1996)
4. [Tablas comparativas por caso de uso](#4-tablas-comparativas-por-caso-de-uso)
5. [Anti-patrones y trampas comunes](#5-anti-patrones-y-trampas-comunes)
6. [Cuando NO usar este skill](#6-cuando-no-usar-este-skill)

---

## 1. Criterios de decision rapida

```
                 +-- Europea? -- Si --> Sonrisa/skew? -- Si --> Heston
                 |                                   \-- No --> BS
  Opcion que     |
  quiero         +-- Americana? -- Sin dividendos? -- Si --> BS2
  pricear ------ |                                \-- No --> BS2 o Binomial
                 |
                 +-- Smile + tail risk? -- Si --> Bates
                 |
                 +-- Payoff custom? -- Si --> MC o LSM
                 |
                 +-- Validacion? -- Si --> Binomial N=2000
```

**Reglas rapidas:**

| Situacion | Metodo | Por que |
|-----------|--------|---------|
| Backtest masivo de europeas | `bs` | 419k ops/sec, 0 error |
| Backtest masivo de americanas | `bs2` | 276k ops/sec, ~0.5% error |
| Backtest con sonrisa del mercado | `heston` | 2.5k ops/sec, captura skew |
| Backtest con crash risk real | `bates` | 160 ops/sec, captura colas pesadas |
| Validar otro modelo (sanity check) | `binomial --steps 2000` | Gold standard, 0.1% error |
| Opcion path-dependent (asian, barrier) | `mc` con payoff custom | Framework extensible |
| Necesito prob de ejercicio temprano | `lsm` con paths=50k | Unica opcion via simulacion |

---

## 2. Tabla maestra: precision, velocidad, supuestos

Inputs del benchmark: `S=K=100, T=0.25, r=0.05, sigma=0.20, q=0`.
Medido en Python 3.14 + numpy 2.4.4, Windows 11. **No asumido: medido con
`time.perf_counter()` sobre las funciones reales del skill.**

| Metodo | Funcion | Time complexity | us/op | ops/sec | Supuestos clave | Error tipico |
|--------|---------|-----------------|------:|--------:|-----------------|--------------|
| Black-Scholes | `bs_price` | O(1) | 2.4 | 419k | GBM, vol cte, sin sonrisa | 0 (closed) |
| BS2/BAW | `bs2_american_price` | O(1) | 3.6 | 276k | BS + smooth-pasting, sin sonrisa | <1% vs binomial |
| Binomial CRR N=500 | `binomial_price` | O(N^2) | 5612 | 178 | Discretizacion del GBM | ~0.5% |
| Binomial CRR N=2000 | `binomial_price` | O(N^2) | 31004 | 32 | Idem, mas preciso | ~0.1% |
| Trinomial N=500 | `trinomial_price` | O(N^2) | 9364 | 107 | 3 nodos por paso | ~0.3% |
| MC paths=10k | `mc_european_price` | O(paths) | 1270 | 788 | Sampleo iid + antithetic | ~1% (stderr) |
| MC paths=100k | `mc_european_price` | O(paths) | 5636 | 177 | Idem, mas preciso | ~0.1% (stderr) |
| LSM paths=10k | `lsm_price` | O(paths * steps) | ~150k | ~7 | Regresion polinomial | ~1-2% |
| Heston | `heston_price` | O(N_GL) ~ O(1) | 398 | 2.5k | Vol estocastica (CIR), sonrisa via rho | <0.1% vs QuantLib |
| Bates | `bates_price` | O(15) = 6 ms | 6241 | 160 | Heston + Merton jumps | <0.5% |
| Greeks (BS) | `bs_greeks` | O(1) | 3.9 | 257k | Formulas cerradas | 0 (closed) |
| P(ITM) | `prob_itm` | O(1) | 1.1 | 908k | N(d2) bajo Q | 0 (closed) |
| IV solve | `implied_vol` | O(log(1/eps)) | 82 | 12k | Bisection sobre BS o binomial | 1e-7 |

---

## 3. Por que de cada metodo

### 3.1 Black-Scholes

**Por que existe**: Es el **standard de la industria** para europeas. Closed-form,
exacta bajo sus supuestos. Es la base sobre la cual se construye todo lo demas.

**Por que usarlo**:
- **Performance imbatible**: 419k opciones/seg en Python puro. 100x mas rapido
  que cualquier alternativa no-closed-form.
- **Simplicidad**: solo 5 inputs (S, K, T, r, sigma). Trivial de implementar
  y verificar.
- **Greeks closed-form**: delta, gamma, vega, theta, rho todos disponibles
  via formulas analiticas. Imbatible para hedging.
- **Calibracion trivial**: solo hay un parametro libre (sigma) por opcion.

**Por que NO usarlo**:
- **Asume volatilidad constante**: la sonrisa de vol del mercado real
  (skew, term structure) NO existe en BS. Backtestear con BS + IV fija da
  errores sistematicos en wings.
- **Asume distribucion lognormal**: retornos reales tienen **skew negativo**
  y **kurtosis > 3** (fat tails). BS subestima el riesgo de crash.
- **Solo europeas**: no funciona para opciones americanas (early exercise).

**Cuando es la eleccion correcta**:
- Backtest de **masas** de opciones vanilla europeas
- Greeks analiticos para **delta-hedging**
- Cuando la **velocidad** importa mas que la precision en wings
- Como **baseline** para comparar contra modelos mas complejos

**Tabla de decision**:

| Si tenes... | Usa... |
|-------------|--------|
| 1M opciones, T<1y, ATM | BS (no hay nada mas rapido) |
| Opcion con strike > 1.5x o < 0.7x ATM | NO BS (sonrisa importa) |
| Portfolio con tail risk real | NO BS (subestima crashes) |

---

### 3.2 Bjerksund-Stensland 2002 / BAW

**Por que existe**: BS asume ejercicio solo en T. Para americanas (ejercicio
en cualquier t) necesitamos otra cosa. BAW/BS1993 es la version **rapida
y closed-form** para americanas.

**Por que usarlo**:
- **O(1) closed-form**: 276k ops/sec, comparable a BS. 1000x mas rapido
  que el binomial.
- **Buena precision**: ~0.5% vs binomial N=2000. Suficiente para backtest.
- **Robusto**: no necesita libs externas, no tiene ramas fragiles.
- **Funciona para call y put** (con swap put-call para el caso put).

**Por que NO usarlo**:
- **Mismo problema de sonrisa que BS**: asume vol constante. Para
  backtesting serio, combinar BS2 con Heston o Bates.
- **Limite en q >= r**: cuando dividend yield > risk-free, BAW no converge
  y se cae a binomial (mas lento). La implementacion tiene este fallback.
- **Limite en put con q=0**: la simetria put-call degenera. Fallback a
  binomial.
- **~0.5% error** vs 0% de BS: para algunas estrategias la diferencia importa.

**Cuando es la eleccion correcta**:
- Backtest masivo de **opciones americanas**
- Cuando necesitas O(1) por opcion para iterar rapido
- Como **primera aproximacion** antes de refinar con binomial

**Tabla de decision**:

| Si tenes... | Usa... |
|-------------|--------|
| Americana, ATM, |q-r| < 5% | BS2 (rapido, preciso) |
| Americana, ATM, |q-r| > 5% | Binomial (BS2 fallback) |
| Americana, deep ITM/OTM | Binomial N=2000 (mas preciso) |

---

### 3.3 Binomial CRR

**Por que existe**: **El gold standard** de validacion. Converge a la solucion
exacta de la EDP de Black-Scholes cuando N -> inf. Para N=2000-10000,
el error es <0.05%.

**Por que usarlo**:
- **Convergencia probada**: a diferencia de BAW o Heston (que son
  aproximaciones), binomial converge a la solucion verdadera.
- **Americanas + Europeas**: el mismo algoritmo funciona para ambas.
- **Simple de entender**: la intuicion del arbol up/down es muy clara.
- **Vectorizable**: el backward induction es O(N^2) con numpy. Para N=500,
  5.6 ms/op.

**Por que NO usarlo**:
- **Lento**: 5.6 ms/op (vs 3.6 us para BS2). ~1500x mas lento.
- **No captura sonrisa**: mismo problema que BS. Asume lognormal.
- **Oscilacion de precios**: a veces converge erraticamente. Hay que
  promediar N=500 y N=1000 (Richardson extrapolation) para resultados
  confiables.

**Cuando es la eleccion correcta**:
- **Validacion** de otros modelos (siempre comparar contra binomial N=2000)
- Americana con parametros extremos (donde BAW no aplica)
- Calculo de greeks por diferencias finitas (delta, gamma, vega)
- Cuando la **precision** importa mas que la velocidad

**Tabla de decision**:

| Si necesitas... | Usa... |
|-----------------|--------|
| Validar otro pricer | Binomial N=2000 |
| Opcion americana con q >= r | Binomial N=1000 |
| Greeks por diferencias finitas | Binomial N=200+ |
| Backtest masivo (>10k opciones) | NO binomial (usar BS2) |

---

### 3.4 Trinomial Boyle

**Por que existe**: Variante del binomial con **3 nodos por paso** (up, middle,
down). Mejor condicionamiento numerico que CRR.

**Por que usarlo**:
- **Convergencia mas monotona**: vs CRR que oscila. ~30% menos pasos para
  misma precision.
- **Mejor para T largos y sigma altos**: donde CRR diverge erraticamente.
- **Sirve para validar binomial**: si los dos coinciden, tenes confianza.

**Por que NO usarlo**:
- **~1.7x mas lento** que binomial para mismo N. Si binomial ya es lento,
  trinomial es peor.
- **No captura sonrisa**.
- **Complejidad adicional** sin beneficio dramatico para backtest tipico.

**Cuando es la eleccion correcta**:
- Cuando binomial da resultados erraticos (validacion cruzada)
- Opciones de largo plazo (T > 2 anos)
- Volatilidades altas (sigma > 100%)

**En general**: usa binomial primero. Trinomial solo si binomial falla.

---

### 3.5 Monte Carlo antithetic

**Por que existe**: Cuando el payoff **no es closed-form** (asian, lookback,
barrier, multi-asset basket) y no se puede escribir como una funcion de S_T,
se necesita simulacion.

**Por que usarlo**:
- **Framework extensible**: payoff custom = solo cambiar la funcion
  de pago. El resto del codigo es igual.
- **Antithetic variates**: reduce varianza 50-70% (factor 2-3x en
  samples efectivos).
- **Convergencia O(1/sqrt(N))**: aceptable para aplicaciones no-time-critical.

**Por que NO usarlo**:
- **Lento para vanilla**: 1.3 ms (paths=10k) vs 2.4 us para BS. 540x mas
  lento para **menos** precision.
- **No captura sonrisa** (mismo drift risk-neutral que BS).
- **Ruido estocastico**: cada corrida da un resultado distinto. Para
  resultados reproducibles, fijar `--seed`.

**Cuando es la eleccion correcta**:
- **Opciones exoticas** (asian, barrier, lookback) que el skill no implementa
  pero el framework soporta
- **Multi-asset** (basket, spread, rainbow) que requieren paths correlacionados
- **Validacion** de otros modelos (como sanity check)
- **Stress testing** con payoffs custom

**Tabla de decision**:

| Si necesitas... | Usa... |
|-----------------|--------|
| Vanilla europea, ATM | NO MC (usar BS) |
| Vanilla europea, deep OTM | MC con paths=10k (BS es exacto pero tarda similar) |
| Opcion con payoff custom | MC (es el unico que aplica) |
| Validacion rapida | MC con seed fija, paths=100k |

---

### 3.6 Longstaff-Schwartz

**Por que existe**: LSM extiende MC a **opciones americanas** usando
regresion least-squares para estimar el valor de continuacion. Es el
metodo de simulacion standard para americanas.

**Por que usarlo**:
- **Unico MC para americanas**: cuando BS2 no aplica (payoff custom,
  multi-asset).
- **Lower bound del precio verdadero**: LSM da un subestimador. Si tenes
  upper bound (dual LSM), acotas el precio real.
- **Funciona con payoffs custom**: igual que MC, pero con decision de
  ejercicio en cada nodo.

**Por que NO usarlo**:
- **Lentisimo**: 150 ms/op. **41,000x mas lento** que BS2.
- **Necesita muchos paths** para converger (paths=10k da error ~2-3%).
- **Lower bound only**: sin dual LSM no tenes upper bound.
- **Para vanilla americana**: BS2 es 1000x mas rapido y suficiente.

**Cuando es la eleccion correcta**:
- **Americana con payoff custom** (donde BS2 no aplica)
- **Multi-asset basket americano** (donde BAW no aplica)
- **Calibracion** de un modelo de vol donde la put americana es referencia

**Tabla de decision**:

| Si tenes... | Usa... |
|-------------|--------|
| Americana vanilla | BS2 (1000x mas rapido) |
| Americana con payoff custom | LSM (unica opcion) |
| Multi-asset basket americano | LSM (extender framework) |
| Backtest masivo americano | BS2 + ajustar bias si es necesario |

---

### 3.7 Heston 1993

**Por que existe**: BS asume **volatilidad constante**. La realidad es que
la vol tiene:
- **Skew** (asimetría): puts mas caros que calls (mercado paga por
  proteccion contra caidas)
- **Term structure**: vol distinta para cada expiry
- **Smile**: la sonrisa alrededor del ATM

Heston captura **skew** y parte de la **term structure** modelando la vol
como un proceso estocastico (CIR).

**Por que usarlo**:
- **Captura sonrisa real**: el parametro `rho` (correlacion spot-vol)
  produce skew negativo (tipico -0.5 a -0.8 en equity). Es el efecto
  cuantitativamente mas importante que BS pierde.
- **O(1) closed-form** via Fourier integral (~400 us, comparable a BS).
- **Calibrable**: los 5 parametros (v0, kappa, theta, sigma_v, rho) se
  pueden fitear a una superficie de vol real.
- **Vol mean-reversion**: el parametro `kappa` (tipico 0.5-3) hace que la
  vol tienda a `theta` (vol de largo plazo). Captura term structure.

**Por que NO usarlo**:
- **Lento vs BS**: 400 us vs 2.4 us. **~165x mas lento** que BS.
- **No captura colas pesadas**: el proceso CIR es gaussiano-impulsado,
  no permite jumps. Subestima riesgo de crash.
- **Calibracion dificil**: 5 parametros en 5D optimization. Hay minimos
  locales. Requiere regularizacion.
- **Spread smile**: Heston tiene dificultad para fitear sonrisas muy
  empinadas (las opciones deep OTM). Para eso: local vol (Dupire) o
  Bates.

**Cuando es la eleccion correcta**:
- **Backtest con sonrisa** del mercado (necesitas skew para que las
  opciones deep OTM/ITM tengan sentido)
- **Calibracion** de un modelo de vol
- **Pricing de opciones vanilla** cuando tenes la superficie de vol
- **Comparacion contra BS**: para ver cuanto te perdés por ignorar skew

**Tabla de decision**:

| Si tenes... | Usa... |
|-------------|--------|
| Opcion ATM europea | BS (10x mas rapido) |
| Opcion OTM/ITM europea | Heston (captura skew) |
| Vol surface real (data) | Heston (calibrar y pricer) |
| Cola izquierda importante (crash risk) | Bates (no Heston) |
| Opciones con smile muy pronunciado | Local vol o Bates |

**Parametros tipicos para equity US** (SPY, single names):
- `v0 = 0.04` (vol 20% squared)
- `kappa = 2.0` (mean-reversion ~6 meses)
- `theta = 0.04` (vol de largo plazo 20%)
- `sigma_v = 0.3` (vol de vol, 30% puntos)
- `rho = -0.7` (skew negativo pronunciado)

---

### 3.8 Bates 1996

**Por que existe**: Heston + Merton jumps. Captura **dos fenomenos del
mercado real** que BS/BS2 no capturan:
- **Skew** (via Heston: `rho` negativo)
- **Cola izquierda** (via Merton jumps: `mu_J` negativo, `lambda` > 0)

**Por que usarlo**:
- **Captura crash risk real**: el mercado paga prima extra por proteccion
  contra caidas bruscas. Bates captura esa prima.
- **Smile empinada**: Bates fitetea mejor que Heston puro para opciones
  deep OTM/ITM (los jumps agregan flexibilidad).
- **O(1) con serie**: 15 terminos Poisson convergen rapido. ~6 ms/op.
- **Calibrable**: 8 parametros (5 Heston + 3 jumps: lambda, mu_J, sigma_J).

**Por que NO usarlo**:
- **El mas lento de los closed-form**: 6 ms/op (15 Heston calls). **~2500x
  mas lento** que BS.
- **Calibracion muy dificil**: 8 parametros. Requiere regularizacion fuerte
  y datos abundantes.
- **Overkill para backtest de vanilla**: si los datos historicos ya tienen
  la sonrisa incorporada, no necesitas Bates.
- **No captura stochastic vol-of-vol**: a diferencia de Heston-Nandi o
  Bergomi (modelos de rough vol).

**Cuando es la eleccion correcta**:
- **Backtest con eventos extremos**: FOMC, earnings, market crashes
- **Pricing de opciones con cola izquierda importante** (puts deep OTM
  en indices)
- **Calibracion con datos que muestran jumps** (2010 flash crash, 2020
  COVID, etc)
- **Risk management** de portafolios con exposicion a tail risk

**Tabla de decision**:

| Si tenes... | Usa... |
|-------------|--------|
| Opcion ATM vanilla | BS (1000x mas rapido) |
| Opcion OTM/ITM vanilla, smile normal | Heston (10x mas rapido que Bates) |
| Opcion OTM/ITM con crash risk real | Bates |
| Cola izquierda + smile | Bates |
| Stress testing | Bates con `mu_J=-0.10, sigma_J=0.20` |

**Parametros tipicos para equity US**:
- Heston: como arriba
- `lambda = 1.0` (1 salto esperado por ano, ~media para SPX)
- `mu_J = -0.05` (saltos negativos pequenos, ~5% down)
- `sigma_J = 0.10` (vol de los saltos, 10%)

---

## 4. Tablas comparativas por caso de uso

### Backtest masivo (>10k opciones)

| Metodo | ops/sec | Smile | Cola pesada | Comentario |
|--------|--------:|------|-------------|------------|
| **BS** | 419k | NO | NO | Solo para ATM, europeas |
| **BS2** | 276k | NO | NO | Americanas, O(1) |
| **Heston** | 2.5k | SI | NO | Mejor balance speed/smile |
| **Bates** | 160 | SI | SI | Mas realista pero 15x mas lento |
| **Binomial** | 32-178 | NO | NO | Solo para validacion |

**Regla**: para backtest masivo, **siempre** BS o BS2 a menos que necesites
smile ocola pesada. Usar Heston solo cuando la sonrisa importa.

### Pricing de opcion individual (1 opcion)

Si tenes un unico strike/expiry y queres precision:

| Objetivo | Metodo | Tiempo |
|----------|--------|--------|
| ATM europea | BS | 2.4 us |
| OTM/ITM europea (con skew) | Heston | 400 us |
| Americana con dividendos | BS2 (o Binomial si q>=r) | 4 us o 5 ms |
| Con crash risk | Bates | 6 ms |
| Validacion | Binomial N=2000 | 31 ms |

### Greeks

| Metodo | Computa | Tiempo | Comentario |
|--------|---------|--------|------------|
| `bs_greeks` (BS closed-form) | 5 greeks | 4 us | Solo europeos |
| Finite differences sobre BS | 5 greeks | ~10 us | Funciona con cualquier pricer |
| Finite differences sobre Heston | 5 greeks | ~1.6 ms | Captura smile en greeks |
| Finite differences sobre Bates | 5 greeks | ~30 ms | Mas realista pero caro |

### Implied Volatility

| Metodo | Engine | Tiempo | Comentario |
|--------|--------|--------|------------|
| `iv` con BS | Bisection sobre BS | 82 us | Standalone |
| `iv` con Binomial | Bisection sobre Binomial N=500 | ~3 ms | Para IV de americanas |
| Manual sobre Heston | Newton sobre Heston | ~1 ms | Para IV con sonrisa |

### IV con sonrisa (parametros Heston calibrados)

Para pricar una opcion con la sonrisa implicita por Heston calibrado:

1. Calibrar Heston al surface una vez (offline, scipy.optimize)
2. Usar `heston_price` con los parametros calibrados (~400 us por opcion)
3. Para backtest masivo: precomputar el modelo calibrado y pricar en batch

**Alternativa**: usar el modulo de IV standalone sobre BS para cada opcion,
y aplicar la sonrisa via un factor de ajuste. Mas rapido pero menos
preciso.

---

## 5. Anti-patrones y trampas comunes

### Anti-patrones de uso

**Anti-patron #1**: Usar binomial para backtest masivo.

```python
# MAL: 5.6 ms/op, 178 ops/sec
for option in options:
    price = binomial_price(S, K, T, r, q, sigma, 500, 'call', 'european')

# BIEN: 2.4 us/op, 419k ops/sec
for option in options:
    price = bs_price(S, K, T, r, q, sigma, 'call')
```

**Anti-patron #2**: Usar LSM para americana vanilla.

```python
# MAL: 150 ms/op (cuando BS2 es 3.6 us)
price = lsm_price(S, K, T, r, q, sigma, 'put', paths=10000, steps=50)

# BIEN: 3.6 us/op (mismo resultado, 40,000x mas rapido)
price = bs2_american_price(S, K, T, r, q, sigma, 'put')
```

**Anti-patron #3**: Asumir que BS2 es "tan exacto como BS".

```python
# MAL: BS2 tiene ~0.5% error. Para arbitraje, eso importa.
arb_edge = market_price - bs2_american_price(...)

# BIEN: validar contra binomial para arbitraje
ref = binomial_price(S, K, T, r, q, sigma, 2000, 'put', 'american')
arb_edge = market_price - ref
```

**Anti-patron #4**: Usar MC con pocos paths para validar.

```python
# MAL: 1% de ruido en el "ground truth"
mc_ref = mc_european_price(S, K, T, r, q, sigma, 'call', 1000, seed=42)

# BIEN: paths >= 100k para ruido < 0.1%
mc_ref = mc_european_price(S, K, T, r, q, sigma, 'call', 100000, seed=42)
```

**Anti-patron #5**: No fijar seed en MC/LSM.

```python
# MAL: cada corrida da resultado distinto
mc = mc_european_price(...)

# BIEN: reproducibilidad
mc = mc_european_price(..., seed=42)
```

**Anti-patron #6**: Pagar prima de sonrisa con BS.

```python
# MAL: para deep OTM put, BS subestima el precio porque no ve el skew
put_price = bs_price(S, 0.7*K, T, r, q, sigma, 'put')  # muy barato

# BIEN: usar Heston (que captura skew negativo)
put_price = heston_price(S, 0.7*K, T, r, q, sigma,
                          v0=sigma**2, kappa=2, theta=sigma**2,
                          sigma_v=0.3, rho=-0.7, opt_type='put')
```

### Trampas matematicas

**Trampa #1**: Asumir que P(ITM) risk-neutral = frecuencia real-world.

La P(S_T > K) bajo Q usa drift `r-q`. La frecuencia real-world usa
la drift historica (que puede ser muy distinta). Para backtest de
frecuencia, usar la drift esperada real como input.

**Trampa #2**: Asumir put-call parity para americanas.

P_am - C_am = S*exp(-qT) - K*exp(-rT) **NO** se cumple exactamente para
americanas. Hay una cota pero no igualdad. Para la diferencia exacta,
usar BAW o binomial en ambos lados.

**Trampa #3**: Heston Feller condition.

Heston asume que `2*kappa*theta > sigma_v^2` (Feller condition). Si
no se cumple, la varianza puede tocar 0. Numericamente estable pero
conceptualmente problematico. Calibrar con cuidado.

**Trampa #4**: Bates con `lambda` muy alto.

Si `lambda*T > 30` (mas de 30 saltos esperados), la serie Poisson
converge muy lentamente y se necesita `n_terms` > 50. Performance se
degrada linealmente con `n_terms`.

---

## 6. Cuando NO usar este skill

- **Opciones path-dependent complejas** (asian lookback, chooser,
  compound): el framework MC se puede extender pero el skill no las
  implementa out-of-the-box.
- **Multi-asset** (basket, spread, rainbow): el skill no soporta
  correlacion entre subyacentes. Usar QuantLib o implementar MC custom.
- **Modelos de rough volatility** (Bergomi, rBergomi): no implementados.
  Para estos, usar libreria especializada.
- **Interest rate options** (caps, floors, swaptions): el modelo subyacente
  es diferente (Hull-White, Black 76). Usar skill dedicado.
- **Credit derivatives** (CDS, CDO): no implementado.
- **High-frequency pricing** (microsegundos): Python no es el lenguaje
  correcto. Usar C++/Rust o libreria QuantLib en C.

Para todos estos casos, **el framework es extensible**: copiar el skill,
agregar las funciones, mantener la estructura.

---

## Resumen ejecutivo

1. **Para backtest de vanilla europea**: BS. Sin dudarlo. 419k ops/sec.
2. **Para backtest de vanilla americana**: BS2. 276k ops/sec.
3. **Si necesitas sonrisa (skew real)**: Heston. 2.5k ops/sec.
4. **Si necesitas cola izquierda (crash risk)**: Bates. 160 ops/sec.
5. **Para validar cualquier otro modelo**: Binomial N=2000. Gold standard.
6. **Para payoffs custom**: MC con seed fija y paths >= 10k.
7. **Para americana con payoff custom**: LSM, paciencia.
8. **Para calibrar un modelo**: Heston (5 params) o Bates (8 params).

Y siempre: **medir performance con `time.perf_counter()` antes de
asumirla**. La tabla de benchmarks en este documento fue medida, no
asumida.
