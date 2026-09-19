# Spec: Market Data + Strategy Pricing Toolkit (desde cero)

Documento **autocontenido** para implementar un toolkit de **construcción de estrategias con datos de mercado + valuación / escenarios / plots**. Sin UI obligatoria. No asume acceso a ningún repositorio previo.

**Dependencia:** el módulo **Market Data (`core`)** de la spec hermana (`MARKET_DATA_MODULE_SPEC` o equivalente): `get_spot`, `get_options_chain`, `get_expirations`, `get_dividend_yield`, `get_risk_free_rate_with_source`, `calc_implied_vol_atm_with_source` / solver IV.

**Importante — modelos de pricing:** este módulo **NO** implementa BAW / binomial / Monte Carlo / diferencias finitas. Solo define el **contrato del pricer** (`VanillaPricer`) y puntos de inyección. El otro agente (o un paquete de pricing aparte) conecta ahí las funciones reales.

---

## 0. Alcance

| Capacidad | Incluir |
|-----------|---------|
| Cargar ticker → spot, chain, r, div, σ ATM sugerida | sí |
| Catálogo de estrategias con preview y apply | sí (todas las listadas abajo) |
| Legs editables (expiry, strike, tipo, L/S, qty, precios, IV) | sí |
| Pierna de stock (qty + precio comprado) | sí |
| Resumen Mercado HOY / Pagado / P&L | sí |
| IV por leg (manual + calcular BS) | sí |
| Griegas de portfolio (Δ Γ ν Θ) | sí (BS analítico incluido o inyectable) |
| Plot payoff / P&L al vencimiento | sí |
| Matriz de escenarios S × tiempo | sí |
| Curvas P&L por fecha | sí |
| Export Excel (Valor / P&L / %PnL) | sí |
| Implementación de motores BAW/Bin/MC/FD | **no** — solo hooks |

---

## 1. Stack Python

```text
pip install requests pandas numpy matplotlib openpyxl scipy yahooquery yfinance
```

| Paquete | Uso en este módulo |
|---------|-------------------|
| `pandas` | chain, matrices, Excel |
| `numpy` | grillas S, payoff vectorizado, escenarios |
| `matplotlib` | payoff chart + curvas de escenarios |
| `openpyxl` | export `.xlsx` |
| `scipy` | opcional (`norm` para griegas BS); alternativa: implementación CDF propia |
| Market Data toolkit | spot, chain, r, div, IV |

Imports canónicos:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Callable, Literal, Optional, Protocol, Sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm  # opción A para griegas

# Market data (paquete hermano)
from market_data import (
    get_spot,
    get_quote,
    get_expirations,
    get_options_chain,
    get_dividend_yield,
    get_risk_free_rate_with_source,
)
```

---

## 2. Constantes y schemas

```python
LOTES = 100  # multiplicador equity options US (1 contrato = 100 acciones)

PriceSource = Literal["bid", "ask", "last", "mid"]
OptType = Literal["call", "put"]
SideQty = int  # >0 long, <0 short
```

### 2.1 Leg de opción

```python
@dataclass
class OptionLeg:
    expiry: str                 # "YYYY-MM-DD"
    strike: float
    type: OptType               # "call" | "put"
    qty: int                    # signed: +1 long, -1 short
    precio_mercado: float       # mark usado para MTM (según source)
    precio_mercado_source: PriceSource
    precio_pagado: float        # costo de entrada por acción de opción
    sigma: float                # IV decimal por leg (ej. 0.25)
    bid: float | None = None
    ask: float | None = None
    last: float | None = None
```

### 2.2 Posición / estrategia

```python
@dataclass
class StrategyPosition:
    ticker: str
    spot: float
    stock_qty: float = 0.0
    stock_precio_comprado: float = 0.0
    legs: list[OptionLeg] = field(default_factory=list)
    r: float = 0.05
    div: float = 0.0
```

### 2.3 Mid

```text
mid = (bid + ask) / 2   si bid>0 y ask>0; si no, None → caer a last o 0
```

### 2.4 Valores agregados

```text
valor_stock     = stock_qty * spot
valor_opciones  = Σ qty_i * LOTES * precio_mercado_i
mercado_hoy     = valor_stock + valor_opciones

pagado_stock    = stock_qty * stock_precio_comprado
pagado_opciones = Σ qty_i * LOTES * precio_pagado_i
pagado          = pagado_stock + pagado_opciones

pnl_hoy         = mercado_hoy - pagado
```

---

## 3. Catálogo de estrategias (TODAS)

El módulo debe exponer un catálogo con: **id**, **categoría**, **nombre display**, **descripción**, **builder de legs**, flags.

Strikes de referencia (dados spot y `spread_pct` en %):

```text
atm     = strike de la chain más cercano a spot
otm_c1  = más cercano a spot * (1 + spread)
otm_c2  = más cercano a spot * (1 + 2*spread)
otm_p1  = más cercano a spot * (1 - spread)
otm_p2  = más cercano a spot * (1 - 2*spread)
spread  = spread_pct / 100   (default spread_pct = 5)
```

Vencimientos:

- `exp_near`: primer expiry con ≥ 21 días (si no hay, el primero disponible).
- `exp_far`: solo calendars — un expiry estrictamente posterior a `exp_near`.

### 3.1 Direccionales alcistas

| id | Nombre | Legs (qty, type, strike, expiry) |
|----|--------|----------------------------------|
| `long_call` | Long Call | +1 call ATM @ near |
| `bull_call_spread` | Bull Call Spread | +1 call ATM, −1 call otm_c1 @ near |
| `bull_put_spread` | Bull Put Spread | −1 put otm_p1, +1 put otm_p2 @ near |
| `covered_call` | Covered Call | −1 call otm_c1 @ near (**nota:** requiere `stock_qty` > 0) |

### 3.2 Direccionales bajistas

| id | Nombre | Legs |
|----|--------|------|
| `long_put` | Long Put | +1 put ATM @ near |
| `bear_put_spread` | Bear Put Spread | +1 put ATM, −1 put otm_p1 @ near |
| `bear_call_spread` | Bear Call Spread | −1 call otm_c1, +1 call otm_c2 @ near |
| `protective_put` | Protective Put | +1 put ATM @ near (**nota:** requiere stock) |

### 3.3 Neutras / volatilidad

| id | Nombre | Legs |
|----|--------|------|
| `long_straddle` | Long Straddle | +1 call ATM, +1 put ATM @ near |
| `short_straddle` | Short Straddle | −1 call ATM, −1 put ATM @ near |
| `long_strangle` | Long Strangle | +1 call otm_c1, +1 put otm_p1 @ near |
| `short_strangle` | Short Strangle | −1 call otm_c1, −1 put otm_p1 @ near |

### 3.4 Complejas

| id | Nombre | Legs |
|----|--------|------|
| `long_call_butterfly` | Long Call Butterfly | +1 call otm_p1, −2 call ATM, +1 call otm_c1 @ near |
| `iron_condor` | Iron Condor | +1 put otm_p2, −1 put otm_p1, −1 call otm_c1, +1 call otm_c2 @ near |
| `iron_butterfly` | Iron Butterfly | +1 put otm_p1, −1 put ATM, −1 call ATM, +1 call otm_c1 @ near |
| `call_calendar` | Call Calendar Spread | −1 call ATM @ **near** + +1 call ATM @ **far** (`two_expiry=True`) |
| `put_calendar` | Put Calendar Spread | −1 put ATM @ **near** + +1 put ATM @ **far** (`two_expiry=True`) |

### 3.5 Registro adicional de piernas por nombre (pricing compuesto)

Para valuación por nombre (misma IV/T para todas las piernas opcionales), mantener este mapa `(tipo, K, coef)` con `tipo in {"C","P"}`:

| nombre | Piernas | Params |
|--------|---------|--------|
| `bull_call_spread` | (C,K1,+1), (C,K2,−1) | K1\<K2 |
| `bear_call_spread` | (C,K2,+1), (C,K1,−1) | K1\<K2 |
| `bull_put_spread` | (P,K1,+1), (P,K2,−1) | K1\<K2 |
| `bear_put_spread` | (P,K2,+1), (P,K1,−1) | K1\<K2 |
| `straddle` | (C,K,+1), (P,K,+1) | K |
| `strangle` | (C,K1,+1), (P,K2,+1) | típ. K1\>K2 OTM |
| `combo` | (C,K2,+1), (P,K1,−1) | risk reversal |
| `call_butterfly` | (C,K1,+1), (C,K2,−2), (C,K3,+1) | K1\<K2\<K3 |
| `put_butterfly` | (P,K1,+1), (P,K2,−2), (P,K3,+1) | K1\<K2\<K3 |
| `iron_condor` | (P,K1,+1), (P,K2,−1), (C,K3,−1), (C,K4,+1) | K1\<K2\<K3\<K4 |
| `iron_butterfly` | (P,K1,+1), (P,K2,−1), (C,K3,+1), (C,K2,−1) | K1\<K2\<K3 |
| `condor` | (C,K1,+1), (C,K2,−1), (C,K3,−1), (C,K4,+1) | K1\<K2\<K3\<K4 |
| `short_straddle` | (C,K,−1), (P,K,−1) | |
| `short_strangle` | (C,K1,−1), (P,K2,−1) | |
| `ratio_spread` | (C,K1,n1), (C,K2,−n2) | default n1=1,n2=2 |
| `box` | (C,K1,+1), (P,K1,−1), (C,K2,−1), (P,K2,+1) | |
| `covered_call` | (C,K,−1) | stock aparte |
| `protective_put` | (P,K,+1) | stock aparte |
| `collar` | (P,K1,+1), (C,K2,−1) | K1\<K2 |

**Nota:** el catálogo UI (§3.1–3.4) construye legs **heterogéneos** (IV y expiry por leg). El registro §3.5 sirve para `price_named_strategy(...)` con un solo σ/T — ambos deben existir.

Al **aplicar** una estrategia del catálogo:

1. Resolver strikes sobre la chain del `exp_near` (y far si calendar).
2. Rellenar bid/ask/last desde chain; `precio_mercado = mid` (fallback last); `precio_pagado = precio_mercado`; `sigma` inicial = 0.25 (o σ ATM del market data si está disponible).
3. Opción: reemplazar todos los legs o append.

---

## 4. API pública sugerida

```text
# Market bootstrap
load_market(ticker) -> MarketSnapshot
  # spot, quote, expirations, chain DataFrame, div, r(+source), sigma_atm_sugerida

# Estrategias
list_strategies() -> list[StrategyInfo]
build_strategy_legs(strategy_id, spot, strikes, exp_near, exp_far, spread_pct) -> list[OptionLeg]
apply_strategy(position, strategy_id, ..., replace=True) -> StrategyPosition

# Legs CRUD
add_leg(position, leg) / remove_leg / clear_legs
set_leg_price_source(leg, source)   # bid|ask|last|mid → actualiza precio_mercado
lookup_quotes(chain, strike, type, expiry) -> (bid, ask, last)

# IV
calc_leg_iv(leg, spot, r, div, price_source="mid", iv_solver=None) -> float
calc_all_legs_iv(position, ...) -> StrategyPosition
# IV NO se recalcula sola en cada update; solo al pedir calc_* 

# Resumen
summarize(position) -> {mercado_hoy, pagado, pnl_hoy, ...}

# Griegas (BS)
portfolio_greeks(position) -> {delta, gamma, vega, theta, per_leg: [...]}
# stock aporta +stock_qty a delta; opciones × qty × LOTES

# Payoff / plot data
payoff_curve(position, s_lo=None, s_hi=None, n=400) -> PayoffResult
  # S, payoff_total, pnl_total, breakevens, max_pnl, min_pnl, costo_fv
plot_payoff(payoff_result, spot, strikes) -> matplotlib Figure

# Escenarios (HOOK A PRICERS)
build_scenario_grid(...) -> ScenarioGrid
compute_scenarios(position, grid, model_id, pricer_registry, ...) -> ScenarioResult
plot_scenario_curves(result) -> Figure
export_scenarios_xlsx(result, path_or_bytes) -> None
```

---

## 5. IV por leg

Para cada leg:

```text
tipo = "C" si call else "P"
T = max((expiry_date - today).days, 1) / 365
precio = mid o last según price_source del cálculo (usar precio_mercado si ya refleja la source)
sigma = iv_solver(tipo, spot, K, T, r, precio, div)
```

- Solo aceptar `0 < sigma < 5`.
- Botones lógicos: **Calcular IV (leg)** y **Calcular IV (todas)**.
- El widget/campo IV % es editable; **no sobrescribir** IV del usuario en cada refresh salvo tras un calc explícito.

Default solver: Black-Scholes inverso (bisección o `brentq`). Firma:

```python
IvSolver = Callable[[str, float, float, float, float, float, float], float]
# (tipo, S, K, T, r, precio_mercado, div) -> sigma
```

---

## 6. Griegas de portfolio

Por leg (europea BS, analítico):

```text
Δ, Γ, ν (por 1% de σ → vega_raw/100), Θ (por día calendario → theta_anual/365)
```

Agregar:

```text
total_* = Σ qty * LOTES * greek_leg
delta_total += stock_qty
```

Incluir breakdown tabular por leg + fila TOTAL.

**Opción A:** implementar griegas BS en el paquete (`scipy.stats.norm`).  
**Opción B:** inyectar `greeks_fn(tipo, S, K, T, r, sigma, div) -> dict`.

---

## 7. Payoff / P&L al vencimiento (plot)

### 7.1 Fórmulas

```text
S_chart = linspace(S_lo, S_hi, 400)
  S_lo default = 0.80 * min(strikes)   (o 0.8*spot si no hay legs)
  S_hi default = 1.20 * max(strikes)

payoff_opts  = Σ qty_i * LOTES * max(S-K,0)   # calls
             + Σ qty_i * LOTES * max(K-S,0)   # puts
payoff_stock = stock_qty * (S - stock_precio_comprado)
payoff_total = payoff_opts + payoff_stock

T_max = max(días a cada expiry) / 365
costo_fv = pagado * exp(r * T_max)
pnl_total = payoff_total - costo_fv
```

Break-evens: cruces de `pnl_total` por cero (interpolación lineal entre puntos adyacentes).

### 7.2 Plot (matplotlib)

Obligatorio en el resultado gráfico:

1. Área verde `pnl≥0` / roja `pnl<0` (fill_between).
2. Curva payoff sin costo (línea dashed gris).
3. Curva P&L (línea azul gruesa).
4. `axhline(0)`.
5. `axvline(spot)` verde dashed.
6. `axvline(K)` naranja dotted por cada strike distinto.
7. Break-evens: vertical púrpura + anotación `BE $x.xx`.
8. `axhline` max P&L (verde) y min P&L (rojo) dotted.
9. Leyenda sin duplicados; grid suave.

Tabla resumen: max gain, max loss, breakevens, costo FV (+ niveles de S).

---

## 8. Escenarios S × tiempo — HOOK DE MODELOS

### 8.1 Contrato del pricer (conectar aquí)

```python
class VanillaPricer(Protocol):
    def __call__(
        self,
        tipo: Literal["C", "P"],
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        div: float,
        *,
        pasos: int = 100,
        M: int = 150,
    ) -> float:
        """Precio de una opción americana o europea según el motor."""
        ...
```

Registro de modelos (IDs fijos para la UI / API):

| model_id | Nombre display | Kwargs relevantes | Notas |
|----------|----------------|-------------------|-------|
| `baw` | BAW (Barone-Adesi-Whaley) | — | closed-form americana approx |
| `binomial` | Binomial | `pasos` (10–500, default 100) | árbol |
| `monte_carlo` | Monte Carlo | `pasos` / paths (hasta 50k) | |
| `fd` | Diferencias finitas | `M` (20–500, default 150) | |

```python
PRICER_REGISTRY: dict[str, VanillaPricer] = {
    # El implementador de pricing rellena esto:
    # "baw": opcion_americana_baw,
    # "binomial": opcion_americana_bin,
    # "monte_carlo": opcion_americana_mc,
    # "fd": opcion_americana_fd,
}
```

Si un `model_id` no está registrado → `NotImplementedError` con mensaje claro: *"Conectar pricer para model_id=..."*.

**Payoff intrinsic cuando `T_eff <= 0`:** no llamar al pricer; usar `max(S-K,0)` / `max(K-S,0)`.

### 8.2 Grilla

Parámetros:

| Param | Default | Rango |
|-------|---------|-------|
| `n_cols` (tiempos) | 4 | 2–20 |
| `n_rows` (precios S) | 11 | 3–51 (impar preferible) |
| `S_desde`, `S_a` | rango del payoff | >0 |

Construcción de tiempos (años restantes hasta el **último** expiry de los legs):

```text
T_max_days = (expiry_max - today).days
T_max = T_max_days / 365

t_vals = [T_max * (n_cols-1-i) / max(1, n_cols-1) for i in range(n_cols)]
# Insertar punto extra cerca del vencimiento para transición suave:
if n_cols >= 2:
    t_vals = t_vals[:-1] + [T_max / max(1,n_cols-1) * 0.5, 0.0]
```

Columnas etiquetadas como **fechas** `dd/mm/yy`:

- col 0 = hoy  
- col última = expiry_max  
- intermedias = interpolación lineal de días  

Filas: `S = linspace(S_desde, S_a, n_rows)`, índice display `S=xx.x` (invertir filas al mostrar: S alto arriba).

### 8.3 Celda (i, j)

Para cada `(S, T)` en la grilla (donde `T` es “años desde hoy hasta esa columna” en el sentido del vector `t_vals` anterior — ver implementación reference abajo):

```text
sv = stock_qty * S
ov = 0
for each leg:
    T_leg = max(days_to_leg_expiry, 0) / 365
    T_eff = T_leg - T_max + T     # tiempo residual de ESA opción en esa columna
    if T_eff <= 0:
        p = intrinsic(tipo, S, K)
    else:
        p = pricer(tipo, S, K, T_eff, r, leg.sigma, div, pasos=..., M=...)
    ov += qty * LOTES * p
mat[i,j] = sv + ov
```

`leg.sigma` es **por leg** (no un σ global).

### 8.4 Matrices derivadas

```text
df_valor = mat
df_pnl   = mat - costo_pagado
costo_fv = costo_pagado * exp(r * T_max)
df_pct   = df_pnl / costo_fv * 100
```

Vistas: **PnL** (ref=0) | **Valor** (ref=costo_pagado) | **%PnL** (ref=0).

### 8.5 Estilo heatmap (tabla)

Degradado:

- `v < ref` → rojo `rgba(220,53,69, alpha)`  
- `v > ref` → verde `rgba(40,167,69, alpha)`  
- `alpha` escala con distancia al ref (≈0.2–0.8)

Columnas con labels únicos (si fechas duplican, sufijo `_1`, `_2`).

### 8.6 Plot de curvas de escenario

Una curva P&L vs S por cada columna/fecha:

- Primera y última columna: linewidth mayor, linestyle sólido.  
- Intermedias: dashed.  
- `axhline(0)`, `axvline(spot)`, `axvline(K)` por strikes.  
- Colormap `tab10`.

### 8.7 Cálculo bajo demanda

`compute_scenarios` **solo** al invocarse explícitamente (botón / API call). Cachear por hash de:

```text
(n_rows, n_cols, S_desde, S_a, model_id, pasos, M, r, div, stock_qty, stock_comprado,
 tuple(strike, qty, expiry, sigma) por leg)
```

Invalidar cache si cambian params o sigmas.

### 8.8 Export

Excel con 3 sheets: `Valor estrategia`, `P&L`, `%PnL`. Engine `openpyxl`.

---

## 9. Flujo end-to-end (lógica, no UI)

```text
1. load_market("AAPL")
2. list_strategies() → elegir "iron_condor"
3. apply_strategy(..., spread_pct=5, replace=True)
4. (opcional) editar legs / stock_qty
5. calc_all_legs_iv(...)
6. summarize(position)
7. portfolio_greeks(position)
8. payoff_curve + plot_payoff
9. Registrar PRICER_REGISTRY["baw"] = ...   # ← conexión externa
10. compute_scenarios(position, grid, model_id="baw", ...)
11. plot_scenario_curves + export_scenarios_xlsx
```

---

## 10. Layout del paquete

```text
strategy_lab/   # o market_data_pricing/
  __init__.py
  schemas.py
  catalog.py          # STRATEGY_CATALOG + ESTRATEGIA_PIERNAS
  position.py         # load_market glue, CRUD legs, summarize
  iv.py               # calc_leg_iv / calc_all
  greeks.py           # BS portfolio greeks
  payoff.py           # curve + breakevens + plot
  scenarios.py        # grid + compute (usa VanillaPricer)
  pricers.py          # Protocol + PRICER_REGISTRY vacío + register_pricer()
  export.py           # xlsx
  plots.py            # helpers matplotlib
```

```python
# pricers.py
def register_pricer(model_id: str, fn: VanillaPricer) -> None:
    PRICER_REGISTRY[model_id] = fn

def get_pricer(model_id: str) -> VanillaPricer:
    if model_id not in PRICER_REGISTRY:
        raise NotImplementedError(
            f"No hay pricer registrado para '{model_id}'. "
            f"Disponibles: {list(PRICER_REGISTRY)}. "
            f"Usar register_pricer('{model_id}', tu_funcion)."
        )
    return PRICER_REGISTRY[model_id]
```

---

## 11. Tests de aceptación

```python
# Catálogo completo
ids = {s.id for s in list_strategies()}
assert "iron_condor" in ids and "call_calendar" in ids and "covered_call" in ids

# Piernas iron condor: 4 legs, signs correctos
legs = build_strategy_legs("iron_condor", spot=100, strikes=list(range(80, 121)),
                           exp_near="2026-09-18", exp_far="2026-12-18", spread_pct=5)
assert len(legs) == 4

# Resumen
pos = StrategyPosition(ticker="TEST", spot=100, legs=legs, stock_qty=0)
s = summarize(pos)
assert "mercado_hoy" in s and "pnl_hoy" in s

# Payoff
pr = payoff_curve(pos)
assert pr.S.shape[0] == 400
assert len(pr.breakevens) >= 0

# Escenarios sin pricer → error claro
try:
    compute_scenarios(pos, grid, model_id="baw", ...)
    assert False
except NotImplementedError:
    pass

# Con stub pricer
register_pricer("baw", lambda tipo,S,K,T,r,sigma,div,**kw: max(S-K,0) if tipo=="C" else max(K-S,0))
res = compute_scenarios(pos, grid, model_id="baw")
assert res.df_pnl.shape[0] == grid.n_rows
```

Integration (live market data): `load_market("AAPL")` + apply straddle + `calc_all_legs_iv`.

---

## 12. Entregables

1. Paquete Python con las APIs de §4.  
2. Catálogo completo §3.1–3.5.  
3. `pricers.py` con registry vacío + `register_pricer` (sin BAW/Bin/MC/FD implementados).  
4. Plots matplotlib (payoff + escenarios).  
5. Export Excel.  
6. README: ejemplo end-to-end + cómo conectar un pricer.  
7. `requirements.txt` alineado al Stack.  
8. Tests unitarios (catálogo, payoff, scenarios con stub).

---

## 13. Opciones de diseño (cerradas)

| Tema | Default | Alternativa aceptable |
|------|---------|------------------------|
| Forma API | Funciones + dataclasses | Clase `StrategyLab` que wrappea lo mismo |
| Griegas | BS propio con `scipy.stats.norm` | Inyectar `greeks_fn` |
| Solver IV | Bisección numpy | `scipy.optimize.brentq` |
| Modelos | Registry vacío + 4 IDs | Mismos IDs; stub que lanza `NotImplementedError` hasta `register_pricer` |
| QuantLib | No | Si el consumidor registra `*_ql` bajo los mismos `model_id` |
| UI | Ninguna (librería) | Thin Streamlit/FastAPI aparte que solo llama esta API |
| LOTES | 100 fijo | Param `multiplier` por posición (default 100) |
| Fecha columna escenario | `dd/mm/yy` | ISO `YYYY-MM-DD` (documentar en README) |

---

## 14. Ejemplo: conectar un pricer externo

```python
from strategy_lab import register_pricer, compute_scenarios, build_scenario_grid

def mi_baw(tipo, S, K, T, r, sigma, div, **, pasos=100, M=150):
    # implementar o importar desde paquete de pricing del usuario
    ...

register_pricer("baw", mi_baw)
register_pricer("binomial", mi_binomial)
register_pricer("monte_carlo", mi_mc)
register_pricer("fd", mi_fd)

grid = build_scenario_grid(n_cols=4, n_rows=11, S_desde=80, S_a=120)
result = compute_scenarios(position, grid, model_id="baw")
```

Sin este paso, el módulo de market-data+strategy sigue siendo útil para: cargar mercado, armar estrategias, IV, griegas, payoff y plots — la matriz de escenarios queda lista para enganchar pricing.
