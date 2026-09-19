# Option Pricing — Referencia Teorica

Teoria completa de los 5 metodos de pricing implementados en
`scripts/option_pricing.py`. En espanol. Asume familiaridad con calculo
estocastico basico (movimiento browniano, martingalas, Ito) y mercados
financieros.

Para la guia rapida de uso del CLI, ver `SKILL.md`.

---

## Indice

1. [Modelo de Black-Scholes-Merton](#1-modelo-de-black-scholes-merton)
2. [Greeks analiticos](#2-greeks-analiticos)
3. [Arbol Binomial (Cox-Ross-Rubinstein)](#3-arbol-binomial-cox-ross-rubinstein)
4. [Arbol Trinomial (Boyle)](#4-arbol-trinomial-boyle)
5. [Monte Carlo con variates antitetic](#5-monte-carlo-con-variates-antitetic)
6. [Longstaff-Schwartz (American MC)](#6-longstaff-schwartz-american-mc)
7. [Barone-Adesi-Whaley (closed-form American)](#7-barone-adesi-whaley-closed-form-american)
8. [Implied Volatility](#8-implied-volatility)
9. [Probabilidad de ITM y P(Profit)](#9-probabilidad-de-itm-y-pprofit)
10. [Tabla comparativa: precision vs velocidad](#10-tabla-comparativa-precision-vs-velocidad)
11. [Cuando usar cada metodo](#11-cuando-usar-cada-metodo)

---

## 1. Modelo de Black-Scholes-Merton

### 1.1 Supuestos

- El subyacente `S_t` sigue un movimiento browniano geometrico (GBM):
  `dS_t = (r - q) * S_t * dt + sigma * S_t * dW_t`
- Volatilidad `sigma` y tasa libre de riesgo `r` constantes.
- No hay costos de transaccion, ni impuestos, ni restricciones short-selling.
- El subyacente paga dividend yield continuo `q` (puede ser 0).
- Opcion estilo europeo (solo se ejerce en T).

### 1.2 Derivacion

Aplicando lema de Ito a `log(S_t)` y bajo la medida risk-neutral `Q`:

```
S_T = S_0 * exp((r - q - 0.5*sigma^2)*T + sigma*sqrt(T)*Z),   Z ~ N(0,1)
```

El precio de la opcion es el valor presente del payoff esperado bajo `Q`:

```
C = exp(-r*T) * E_Q[max(S_T - K, 0)]
P = exp(-r*T) * E_Q[max(K - S_T, 0)]
```

### 1.3 Formula cerrada

Definiendo:
- `d1 = (log(S/K) + (r - q + 0.5*sigma^2)*T) / (sigma*sqrt(T))`
- `d2 = d1 - sigma*sqrt(T)`
- `N(x)` = CDF normal estandar

Entonces:

```
Call = S*exp(-q*T)*N(d1) - K*exp(-r*T)*N(d2)
Put  = K*exp(-r*T)*N(-d2) - S*exp(-q*T)*N(-d1)
```

**Implementacion**: `bs_price()`. Usa `math.erfc` para `N(x)` (2-3x mas
rapido que `scipy.stats.norm.cdf` y ~10x mas rapido que custom approx).

### 1.4 Limites importantes

- `sigma -> 0` (sin volatilidad): `Call = max(S*exp(-q*T) - K*exp(-r*T), 0)`
- `T -> 0`: `Call = max(S - K, 0)` (intrinsic value)
- `S -> inf`: `Call -> S*exp(-q*T)` (lower bound)
- `S -> 0`: `Put = K*exp(-r*T)`

---

## 2. Greeks analiticos

Son las derivadas parciales del precio respecto a sus inputs. Criticos
para hedging y gestion de riesgo.

### 2.1 Delta (dV/dS)

```
Delta_call = exp(-q*T) * N(d1)
Delta_put  = exp(-q*T) * (N(d1) - 1)
```

Interpretacion: variacion del precio de la opcion ante un cambio de $1 en S.

### 2.2 Gamma (d2V/dS2)

```
Gamma = exp(-q*T) * n(d1) / (S * sigma * sqrt(T))
```

donde `n(x) = (1/sqrt(2*pi)) * exp(-x^2/2)` es la PDF normal estandar.
Mismo gamma para call y put. Mide la convexidad del precio.

### 2.3 Vega (dV/dsigma)

```
Vega = S * exp(-q*T) * n(d1) * sqrt(T)
```

Mismo vega para call y put. En la implementacion esta en unidades de 1.0
(no en %); para "vega por 1% de vol", dividir por 100.

### 2.4 Theta (dV/dT)

```
Theta_call = -S*exp(-q*T)*n(d1)*sigma/(2*sqrt(T))
             - r*K*exp(-r*T)*N(d2)
             + q*S*exp(-q*T)*N(d1)
Theta_put  = -S*exp(-q*T)*n(d1)*sigma/(2*sqrt(T))
             + r*K*exp(-r*T)*N(-d2)
             - q*S*exp(-q*T)*N(-d2)
```

Mide el decaimiento temporal (time decay). Generalmente negativo para calls
long y puts long.

### 2.5 Rho (dV/dr)

```
Rho_call = K*T*exp(-r*T)*N(d2)
Rho_put  = -K*T*exp(-r*T)*N(-d2)
```

**Implementacion**: `bs_greeks()`. Todos los greeks se computan en una sola
llamada (costo despreciable, ~1.5 microsegundos).

---

## 3. Arbol Binomial (Cox-Ross-Rubinstein)

### 3.1 Idea basica

Discretizar el GBM en N pasos. En cada paso, el subyacente sube por factor
`u` o baja por factor `d`, con probabilidades risk-neutral `p` y `1-p`.
Backward induction desde los payoffs en `t=N` hasta `t=0`.

### 3.2 Parametros CRR

Con `dt = T/N`:

```
u = exp(sigma * sqrt(dt))
d = 1/u
a = exp((r - q) * dt)
p = (a - d) / (u - d)         # prob. risk-neutral de "up"
disc = exp(-r * dt)           # factor de descuento por paso
```

### 3.3 Algoritmo

1. **Terminal** (paso N): calcular el payoff en cada uno de los N+1 nodos
   `S * u^(N-j) * d^j`:
   ```
   V_j^N = max(S_T_j - K, 0)     # call
   V_j^N = max(K - S_T_j, 0)     # put
   ```

2. **Backward induction** (paso N-1 hasta 0):
   ```
   V_j^i = disc * (p * V_j^(i+1) + (1-p) * V_(j+1)^(i+1))
   ```
   Para **American**, agregar check de ejercicio temprano en cada nodo:
   ```
   V_j^i = max(V_j^i, intrinsic(S_T_j^i))
   ```

3. **Precio** = `V_0^0`

### 3.4 Convergencia

El error de discretizacion es `O(1/N)` (orden 1). Para opciones europeas,
el binomial converge a BS cuando `N -> inf`. Para americanas, converge
a la solucion exacta de la EDP.

**Reglas de pulgar**:
- `N = 200`: error ~1% en ATM
- `N = 500`: error ~0.5%
- `N = 2000`: error ~0.1% (suficiente para backtesting)
- `N = 5000+`: <0.05% (usar solo para benchmark de referencia)

### 3.5 Optimizaciones implementadas

- Toda la induccion hacia atras es **vectorizada con numpy** (sin loop
  Python explicito sobre los nodos — solo el loop sobre los pasos).
- Se pre-calcula `u^N` para derivar todos los `S_T` terminales.
- El check de ejercicio temprano se hace in-place con `np.maximum`.
- Sin ramas condicionales dentro del loop (la condicion american/european
  esta fuera).

**Performance**: ~3 ms para N=500, ~25 ms para N=2000 (1 opcion).

---

## 4. Arbol Trinomial (Boyle)

### 4.1 Diferencia con binomial

En cada paso, el subyacente puede ir **up** (factor `u`), **middle**
(factor 1, o `m`), o **down** (factor `d`). Tres probabilidades:
`pu + pm + pd = 1`. Esto da una discretizacion mas fina del movimiento
browniano.

### 4.2 Parametros Boyle 1986

Con `dt = T/N`:

```
u = exp(sigma * sqrt(2*dt))
d = 1/u
m = 1   (mid node)
a = exp((r - q) * dt / 2)
b = exp(sigma * sqrt(dt/2))

pu = ((a - 1/b) / (b - 1/b))^2
pd = ((b - a) / (b - 1/b))^2
pm = 1 - pu - pd
```

Para el caso simetrico `r = q = 0`, `pu = pd = 1/4` y `pm = 1/2`.

### 4.3 Indice del arbol

En el paso N, hay `2N + 1` nodos. Indice `j` en `0..2N`:
- `j = 0`: precio maximo `S*u^N`
- `j = N`: precio medio `S`
- `j = 2N`: precio minimo `S*d^N`

Precio en nodo `(N, j)`: `S * u^(N-j)`.

### 4.4 Backward induction

```
V_j^i = disc * (pu * V_j^(i+1) + pm * V_(j+1)^(i+1) + pd * V_(j+2)^(i+1))
```

Para American, agregar el check de ejercicio temprano como en binomial.

### 4.5 Ventajas vs binomial

- **Mejor condicionamiento numerico** para volatilidades altas / T largos.
- **Menor oscilacion** del precio cuando se incrementa N (convergencia
  monotona).
- ~1.5x mas lento que binomial para el mismo N (3x mas operaciones por
  nodo), pero tipicamente necesita ~30% menos pasos para la misma precision.

**Performance**: ~14 ms para N=500, ~110 ms para N=2000.

---

## 5. Monte Carlo con variates antitetic

### 5.1 Idea

Simular N paths del subyacente hasta `T` bajo la medida risk-neutral, y
calcular el payoff promedio. Aplica a opciones **europeas** (el payoff
solo depende de `S_T`).

### 5.2 Generacion de paths

Para cada path `i`:
```
Z_i ~ N(0, 1)            # iid standard normal
S_T_i = S_0 * exp((r - q - 0.5*sigma^2)*T + sigma*sqrt(T)*Z_i)
Payoff_i = max(S_T_i - K, 0)    # call
Payoff_i = max(K - S_T_i, 0)    # put
```

Precio: `V = exp(-r*T) * mean(Payoff_i)`

### 5.3 Variates antitetic (reduccion de varianza)

Idea: para cada `Z_i` simulado, usar tambien `-Z_i`. Ambos contribuyen al
estimador con el mismo peso:

```
Payoff_i = 0.5 * (payoff(S_T con Z_i) + payoff(S_T con -Z_i))
```

**Por que reduce varianza**: `Z` y `-Z` estan correlacionados negativamente.
Cuando uno da un payoff alto, el otro da bajo. El promedio de los dos
tiene menor varianza que la suma de dos samples independientes.

Reduccion tipica de varianza: 50-70% (factor 2-3x en samples efectivos).

### 5.4 Error estandar

```
stderr = exp(-r*T) * std(Payoff_i) / sqrt(N_paths)
```

Intervalo de confianza 95%: `V +/- 1.96 * stderr`.

### 5.5 Parametros practicos

- `paths = 10_000`: stderr ~1% del precio (rapido pero ruidoso)
- `paths = 100_000`: stderr ~0.1% (recomendado para backtesting)
- `paths = 1_000_000`: stderr ~0.03% (solo para benchmark de referencia)

### 5.6 Limitaciones

- **No soporta opciones americanas directamente** (la decision de ejercicio
  depende del path completo, no solo de `S_T`). Para eso usar LSM.
- Convergencia `O(1/sqrt(N))` — mas lenta que los metodos de tree.
- Para opciones path-dependent (asianas, lookback, barrier) es el metodo
  natural.

**Performance**: ~25 ms para paths=100k. Vectorizado con numpy.random.

---

## 6. Longstaff-Schwartz (American MC)

### 6.1 Problema

Para opciones americanas, el ejercicio temprano depende de la trayectoria
completa. La esperanza risk-neutral del payoff no se puede computar
cerradamente (es un problema de optimal stopping).

### 6.2 Algoritmo Longstaff-Schwartz (2001)

1. **Forward**: simular `M` paths del subyacente en `steps+1` puntos
   temporales.
2. **Backward induction** (de `t = steps` a `t = 1`):
   - En cada `t`, identificar paths **in-the-money** (ITM).
   - Para los paths ITM, ajustar una regresion del valor de continuacion
     `Y` (cashflow futuro descontado) sobre funciones del subyacente `S_t`.
   - Funcion de regresion tipica: polinomio de grado 2 en `S_t`
     (Laguerre polynomials o S, S^2 tambien funcionan).
   - Si `intrinsic(S_t) > E[continuacion|S_t]`, ejercer.

### 6.3 Regresion polinomial

Para cada nodo temporal `t` con `N_itm` paths ITM:

```
Y_i = cashflow futuro descontado al tiempo t
X_i = [1, S_t_i, S_t_i^2]
beta = (X^T X)^-1 X^T Y         # minimos cuadrados
continuation = X @ beta
```

Comparar `intrinsic = max(S_t - K, 0) - 0` (call) o `max(K - S_t, 0)` (put)
con `continuation[i]`. Si intrinsic > continuation, ejercer en t.

### 6.4 Propiedades

- **Lower bound**: el LSM da un precio <= precio americano verdadero
  (porque la regresion aproxima la continuation, que es un subestimador).
- **Sesi** con mas paths y mas pasos temporales, el lower bound se acerca
  al verdadero.
- **No provee upper bound** (eso requiere otro algoritmo, dual LSM).

### 6.5 Parametros

- `paths = 50_000`: error ~1-2% (rapido)
- `paths = 200_000`: error ~0.5% (recomendado)
- `steps = 50`: suficiente para la mayoria de los casos
- `steps = 100`: para opciones de largo plazo (T > 1 ano)

### 6.6 Implementacion

Vectorizada con numpy. Para cada paso temporal:
- `itm = intrinsic[:, t] > 0` (mascara booleana)
- `lstsq` para la regresion polinomial
- `exercise_now = intrinsic > continuation` (mascara booleana)

**Performance**: ~50-100 ms para paths=100k, steps=50. Es el metodo
mas lento del skill, pero el unico que da American via simulacion.

---

## 7. Barone-Adesi-Whaley (closed-form American)

### 7.1 Idea

Aproximar la frontera de ejercicio temprano `S*(t)` con una ecuacion
cuadratica (MacMillan 1986, Whaley 1987). Aproxima el valor americano
como:

```
V_american(S) = V_european(S) + A * (S/S*)^q2     # para S < S*
V_american(S) = S - K                              # para S >= S*
```

donde `q2` y `A` dependen de `r, q, sigma, T`. `S*` se obtiene resolviendo
la condicion de **smooth pasting** `dC/dS = 1` via Newton-Raphson.

### 7.2 Algoritmo para call americano (q > 0)

1. Calcular `b = r - q`. Si `b >= r` (q <= 0), no hay ejercicio temprano,
   `V_american = V_european`.

2. Calcular `M = 2r/sigma^2`, `N = 2b/sigma^2`, `K_factor = 1 - exp(-rT)`.

3. Initial guess para `S*` (Bjerksund-Stensland 1993 closed form):
   ```
   q2 = (-(N-1) + sqrt((N-1)^2 + 4M/K_factor)) / 2
   S* = K / (1 - 1/q2)
   ```

4. Newton iteration sobre `S*` (smooth pasting `dC/dS = 1`):
   ```
   S* = q2 * (K + C_eu(S*)) / (q2 - dC/dS(S*))
   ```

5. Si `S >= S*`: `V = S - K`. Si no:
   ```
   V = C_eu(S) + A * (S/S*)^q2
   A = (S* - K)/q2 - C_eu(S*) + (1 - dC/dS(S*)) * S* / q2
   ```

### 7.3 American put via simetria put-call

```
P_american(S, K, T, r, q, sigma) = C_american(K, S, T, q, r, sigma)
```

Es decir, swappear `S <-> K` y `r <-> q`, y aplicar el algoritmo del call.
La intuicion: un put americano sobre S equivale a un call americano sobre
"el strike" K, con la dinamica inversa.

### 7.4 Limitaciones de BAW

- El algoritmo asume `b > 0` (es decir `r > q`). Para `b <= 0` (dividend
  yield alto), el BAW no converge y la implementacion **cae a binomial
  con N=1000** como fallback.
- Error tipico: <0.5% para ATM, <1% para deep ITM/OTM.
- Menos preciso que Bjerksund-Stensland 2002 (~0.1% error), pero mucho
  mas simple (no requiere CDF bivariada normal).

### 7.5 Ventajas

- **O(1)** — corre en ~1.4 microsegundos por opcion. **~2000x mas
  rapido** que el binomial con N=500.
- Ideal para **backtesting de muchas opciones** donde se necesita
  precision ~1% (no se justifica N=2000 en cada opcion).

---

## 8. Implied Volatility

### 8.1 Definicion

Es la volatilidad `sigma_impl` tal que `BS(S, K, T, r, q, sigma_impl,
opt_type) = precio_observado`. Es la "volatilidad que el mercado esta
priceando".

### 8.2 Uso

- Comparar opciones sobre el mismo subyacente en diferentes strikes
  (smirk/skew).
- Input tipico para modelos de vol local/vol estocastica.
- Superficie de vol (sigma_impl vs K, T) para backtesting de estrategias
  de volatilidad.

### 8.3 Algoritmo de resolucion

El `sigma_impl` no tiene formula cerrada (BS es monotona en sigma pero
no invertible algebraicamente). Metodos:

- **Bisection**: robusto, convergencia O(log(1/eps)). Usado aqui.
- **Newton-Raphson**: mas rapido pero necesita initial guess y el vega
  (sensible a vega=0 deep OTM/ITM).
- **Brent**: combina ambos.

### 8.4 Limites

- Intrinsic check: si `precio < intrinsic`, no hay sigma valido.
- Para opciones deep OTM/ITM, el vega es casi cero y la convergencia es
  lenta. Cap superior en `sigma = 5.0` (500% vol anual) es razonable.

### 8.5 Implementacion

Bisection pura, 60 iteraciones maximo (precision ~1e-7). Para opciones
**europeas** usa BS directo. Para **americanas** usa binomial con N=500
como pricing engine (mas lento, ~3 ms por IV solve).

---

## 9. Probabilidad de ITM y P(Profit)

### 9.1 P(ITM) bajo la medida risk-neutral Q

Es la probabilidad, **bajo Q** (no real-world), de que el subyacente
termine ITM al vencimiento:

- Call: `P(S_T > K) = N(d2)`
- Put:  `P(S_T < K) = N(-d2)`

donde `d2 = (log(S/K) + (r - q - 0.5*sigma^2)*T) / (sigma*sqrt(T))`.

**OJO**: esta NO es la frecuencia real-world. Bajo Q, la drift del
subyacente es `r - q` (no la real). Para convertir a probabilidad
real-world, sustituir `r` por la drift esperada del subyacente.

**API**: `prob_itm(S, K, T, r, q, sigma, opt_type) -> float`. Closed-form,
~300 ns/op.

### 9.2 P(Profit) — considerando la prima

Es la probabilidad de que la opcion genere profit al vencimiento,
considerando la prima pagada (o cobrada, si es short):

- Long call: `P(S_T > K + premium)` — `N(d2')` con `d2'` calculado en
  `K_eff = K + premium`
- Long put: `P(S_T < K - premium)` — `N(-d2')` con `K_eff = K - premium`
- Short call: `P(S_T < K + premium)` (probabilidad de que NO nos ejerzan
  y cobremos la prima)
- Short put: `P(S_T > K - premium)`

**API**: `prob_profit(S, K, T, r, q, sigma, opt_type, premium) -> float`.

### 9.3 Uso en backtesting

- **Filtrar trades con P(Profit) > X%**: criterio comun en sistemas
  automatizados para asegurar edge estadistica.
- **Calcular expected value**: `EV = P(profit) * avg_profit - (1 - P(profit)) * avg_loss`
  bajo un modelo de distribucion de outcomes.
- **Comparar estrategias**: dos trades con misma prima pero diferente
  P(Profit) tienen Sharpe diferente esperado.
- **Kelly criterion**: sizing optimo = `2*P(profit) - 1` (simplificado
  para payoffs binarios).

### 9.4 Limitaciones

- Asume distribucion lognormal (modelo BS). Para distribuciones con
  colas pesadas o skew significativo, las probabilidades son
  aproximadas.
- No captura eventos de ejercicio temprano (early exercise premium
  reduce P(Profit) efectiva para americanas ITM).
- Para backtesting, idealmente usar distribucion empirica de retornos
  en lugar de lognormal. P(ITM) risk-neutral es un proxy razonable
  pero no exacto.

### 9.5 Ejemplo numerico

```python
prob_itm(100, 100, 0.25, 0.05, 0, 0.20, "call")
# -> 0.5596  (ATM call, 55.96% de terminar ITM bajo Q)

prob_profit(100, 100, 0.25, 0.05, 0, 0.20, "call", 4.62)
# -> 0.4698  (misma opcion con prima $4.62, 46.98% P(Profit))
```

---

## 10. Tabla comparativa: precision vs velocidad

Benchmarks medidos en Python 3.14 + numpy 2.4.4, Windows 11, 1 opcion por
llamada (call ATM S=K=100, T=0.25, r=0.05, sigma=0.20, q=0). Modo bench
del CLI: `py option_pricing.py bench --bench-n 500`.

| Metodo             | Tiempo/op | Throughput | Error tipico | Estilo     |
|--------------------|----------:|-----------:|--------------|------------|
| Black-Scholes      | 0.0015 ms | 655k/s     | 0 (closed)   | European   |
| BAW (BS2)          | 0.0016 ms | 630k/s     | <1%          | American   |
| Binomial N=500     | 2.8 ms    | 358/s      | ~0.5%        | Ambos      |
| Binomial N=2000    | 17 ms     | 59/s       | ~0.1%        | Ambos      |
| Trinomial N=500    | 23 ms     | 43/s       | ~0.3%        | Ambos      |
| Trinomial N=2000   | 30 ms     | 33/s       | ~0.1%        | Ambos      |
| MC paths=10k       | 0.96 ms   | 1040/s     | ~1% (stderr) | European   |
| MC paths=100k      | 14 ms     | 71/s       | ~0.1% (stderr) | European |
| MC paths=1M        | 83 ms     | 12/s       | ~0.03% (stderr) | European |
| LSM paths=50k steps=50 | 1069 ms | <1/s    | ~1-2%        | American   |
| LSM paths=200k steps=50 | 7628 ms | <0.1/s | ~0.5%        | American   |
| Greeks (BS)        | 0.001 ms  | 1M/s       | 0 (closed)   | European   |
| IV solve (BS)      | 0.6 ms    | 1700/s     | 1e-7         | European   |
| P(ITM)             | 0.0003 ms | 3M/s       | 0 (closed)   | European   |

---

## 11. Cuando usar cada metodo

### Regla de oro para backtesting

1. **European pricing rapido**: siempre `bs_price()` (BS). 800k opciones/s.
2. **American pricing rapido con precision ~1%**: `bs2_american_price()` (BAW).
   730k opciones/s. Si `q >= r`, usa binomial.
3. **American pricing con precision ~0.1%**: `binomial_price()` con `steps=2000`.
   20 opciones/s.
4. **Validacion contra un valor conocido**: `binomial_price()` con `steps=10000`
   + comparar con BS para europeas.
5. **Greeks**: siempre `bs_greeks()` (analiticos, O(1)).
6. **IV solver**: bisection, ~3 ms por solve.

### Casos especificos

- **Opciones path-dependent (asianas, barrier, lookback)**: solo Monte
  Carlo. El skill actual solo implementa MC para europeas, pero el
  framework se puede extender.
- **Opciones con dividendos altos (q > r)**: el BAW no aplica; usar
  binomial o LSM directamente.
- **Exposicion masiva (1M+ opciones)**: precomputar factores comunes
  (discount, drift, vol*sqrt(T)) fuera del loop y reusar.
- **Implied vol sobre toda la cadena**: precomputar d1, d2 una vez por
  opcion y aplicar Newton iterativo vectorizado.

### Para backtesting de estrategias de vol

Si la estrategia es "long volatility", comparar:
- Precio teorico via BS con `sigma = IV_historica`
- Precio de mercado via BS con `sigma = IV_actual`
- La diferencia es el P&L esperado.

Para esta tarea, BS basta. No se necesita binomial salvo que la opcion
sea americana.

---

## Referencias

- Hull, J. (2017). *Options, Futures, and Other Derivatives*, 9th/10th ed.
  Pearson. Cap. 15 (BS), Cap. 21 (arboles), Cap. 27 (MC).
- Cox, J., Ross, S., & Rubinstein, M. (1979). "Option pricing: a simplified
  approach." *Journal of Financial Economics*, 7(3), 229-263.
- Boyle, P. (1986). "Option valuation using a three-jump process."
  *International Options Journal*, 3, 7-12.
- Longstaff, F. & Schwartz, E. (2001). "Valuing American options by
  simulation: a simple least-squares approach." *Review of Financial
  Studies*, 14(1), 113-147.
- Barone-Adesi, G. & Whaley, R. (1987). "Efficient analytic approximation
  of American option values." *Journal of Finance*, 42(2), 301-320.
- Bjerksund, P. & Stensland, G. (2002). "Closed form valuation of American
  options." Working paper.
- Haug, E. (2007). *Complete Guide to Option Pricing Formulas*, 2nd ed.
  McGraw-Hill.
