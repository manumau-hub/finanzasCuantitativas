---
name: portfolio
description: "Construcción y optimización cuantitativa de portafolios: Markowitz (scipy.optimize + Monte Carlo), Black-Litterman (prior CAPM, views absolutas/relativas, posterior bayesiano), HRP/HERC/NCO (clustering jerárquico, risk parity, NCO con restricciones). Todo flat numpy + scipy, sin Riskfolio-Lib ni PyPortfolioOpt."
license: MIT
---

# Portfolio — Optimización Cuantitativa de Portafolios

Este skill implementa **3 enfoques de optimización de portafolios** desde el material del curso
(notebook `Clase_08_teoria_2025_portafolio.ipynb` y PDF `Portafolios 2025 Ucema.pdf`):

1. **Markowitz / Media-Varianza** — Optimización convexa vía `scipy.optimize`
   + simulación Monte Carlo + frontera eficiente + CML.
2. **Black-Litterman** — Combinación bayesiana de retornos de equilibrio de mercado
   (CAPM inverso) con views del inversor, incluyendo matriz de incertidumbre Ω
   (método Idzorek).
3. **HRP / HERC / NCO** — Construcción jerárquica de portafolios mediante clustering
   (single/complete/average/ward), risk parity y NCO con restricciones.

Todos los scripts usan solo `numpy`, `pandas` y `scipy`. Sin dependencias pesadas.
Este skill es **autónomo**: funciona sin `skills/backtesting`.

Para ratios de performance post-optimización (Sharpe, Sortino, VaR, drawdowns, etc.)
consultar el skill hermana:
[`skills/backtesting`](https://github.com/gauss314/skills/tree/main/skills/backtesting).

Part of the [Gauss314 Skills Repository](https://github.com/gauss314/skills).

---

## File Map

```
skills/portfolio/
├── SKILL.md                           ← Este archivo
├── references/
│   ├── PORTFOLIO_THEORY.md            ← MPT, Markowitz, frontera eficiente (ES)
│   ├── BLACK_LITTERMAN.md             ← BL: prior, views, posterior, omega (ES)
│   ├── HIERARCHICAL.md                ← HRP, HERC, NCO, clustering (ES)
│   └── RISK_MEASURES.md               ← VaR, CVaR, MAD, MSV, DR, MDD (ES)
├── assets/
│   ├── sample_prices.csv              ← Precios multi-activo para ejemplos
│   ├── sample_returns.csv             ← Retornos multi-activo
│   ├── sample_mcaps.json              ← Market caps para Black-Litterman
│   └── defaults.json                  ← Parámetros default
├── scripts/
│   ├── __init__.py
│   ├── portfolio.py                   ← Core: Markowitz, Sharpe, Monte Carlo, frontera
│   ├── black_litterman.py             ← BL: prior, posterior, omega, views
│   ├── hierarchical.py                ← HRP/HERC/NCO: clustering, risk parity, constraints
│   ├── risk_measures.py               ← VaR, CVaR, MAD, MSV, MDD, DR
│   ├── covariance.py                  ← Covarianza: hist, ledoit-wolf, oas, ewma
│   └── cli.py                         ← CLI unificada (12 modos)
└── tests/
    ├── __init__.py
    └── test_portfolio.py              ← Tests + validación contra notebook
```

### Qué hace cada script

| Script | Rol | Funciones clave |
|--------|-----|----------------|
| `portfolio.py` | Core de optimización Markowitz | `max_sharpe_optim`, `min_variance_optim`, `random_portfolios`, `efficient_frontier`, `cml_portfolio`, `asset_stats` |
| `black_litterman.py` | Black-Litterman completo | `market_implied_risk_aversion`, `market_implied_prior_returns`, `bl_posterior_returns`, `omega_idzorek` |
| `hierarchical.py` | HRP / HERC / NCO | `hrp_portfolio`, `herc_portfolio`, `nco_portfolio`, `nco_with_constraints`, `hrp_constraints` |
| `risk_measures.py` | Medidas de riesgo | `var_historic`, `cvar`, `max_drawdown`, `cdar`, `diversification_ratio`, `risk_contribution` |
| `covariance.py` | Estimación de covarianza | `cov_hist`, `cov_ledoit_wolf`, `cov_oas`, `cov_ewma` |

---

## Quick Start

### Markowitz (scipy.optimize)

```bash
# Max Sharpe con 3 activos
py scripts/cli.py markowitz --assets assets/sample_returns.csv

# Con tasa libre de riesgo personalizada
py scripts/cli.py markowitz --assets assets/sample_returns.csv --rf 0.05

# Estadísticas individuales
py scripts/cli.py stats --assets assets/sample_returns.csv
```

### Monte Carlo

```bash
# Simular 10.000 carteras aleatorias
py scripts/cli.py montecarlo --assets assets/sample_returns.csv

# Guardar frontera a CSV
py scripts/cli.py montecarlo --assets assets/sample_returns.csv --save frontier.csv
```

### Frontera Eficiente

```bash
py scripts/cli.py frontier --assets assets/sample_returns.csv --n 50
```

### CML — Leverage y Deleverage

El portafolio tangente (máximo Sharpe) se combina con el activo libre de riesgo
para obtener cualquier punto sobre la Capital Market Line (CML), manteniendo
el mismo Sharpe ratio.

```bash
# Portafolio tangente puro (w=1)
py scripts/cli.py cml --assets assets/sample_returns.csv --weight 1.0

# Deleverage: 60% en tangencia, 40% en Rf (menos riesgo, mismo Sharpe)
py scripts/cli.py cml --assets assets/sample_returns.csv --weight 0.6

# Leverage: pide prestado 50% a Rf, invierte 150% en tangencia (más riesgo, mismo Sharpe)
py scripts/cli.py cml --assets assets/sample_returns.csv --weight 1.5
```

### Black-Litterman

```bash
# Prior: retornos implícitos de mercado (CAPM inverso)
py scripts/cli.py bl-prior --assets assets/sample_returns.csv --market-prices assets/sample_prices.csv --mcaps assets/sample_mcaps.json

# BL completo con views + optimización
py scripts/cli.py bl --assets assets/sample_returns.csv --market-prices assets/sample_prices.csv --mcaps assets/sample_mcaps.json --views '{"BMA": 0.25, "LOMA": 0.4, "MELI": -0.1}' --confidences "0.3,0.5,0.8" --optimize
```

### HRP / HERC / NCO

```bash
# Hierarchical Risk Parity
py scripts/cli.py hrp --assets assets/sample_returns.csv

# Nested Clustered Optimization
py scripts/cli.py nco --assets assets/sample_returns.csv --clusters 3

# NCO con restricciones
py scripts/cli.py nco-con --assets assets/sample_returns.csv --constraints assets/sample_constraints.csv --classes assets/sample_classes.csv
```

### Riesgo

```bash
# Todas las medidas de riesgo
py scripts/cli.py risk --prices assets/sample_prices.csv

# Medida específica
py scripts/cli.py risk --prices assets/sample_prices.csv --measure var
```

---

## Usar como Librería

```python
from scripts.portfolio import *
from scripts.black_litterman import *
from scripts.hierarchical import *

import numpy as np

# --- Markowitz ---
rets = pd.read_csv('assets/sample_returns.csv', index_col=0)
result = max_sharpe_optim(rets, rf=0.045)
print(result['weights'], result['sharpe'])  # pesos óptimos, Sharpe

# --- CML: leverage/deleverage ---
# 60% en tangencia, 40% en Rf (deleverage)
cml = cml_portfolio(rets, rf=0.045, weight_tangency=0.6)
print(cml['ret'], cml['vol'], cml['sharpe'])  # mismo Sharpe que el tangente

# Leverage: 150% en tangencia (pide prestado 50% a Rf)
cml2 = cml_portfolio(rets, rf=0.045, weight_tangency=1.5)
print(cml2['ret'], cml2['vol'], cml2['sharpe'])  # mismo Sharpe

# --- Monte Carlo ---
port_df = random_portfolios(rets, n_portfolios=10000, rf=0.045)
best = port_df.loc[port_df['sharpe'].idxmax()]
print(best['weights'])  # mejor combinación Monte Carlo

# --- Black-Litterman ---
import json
with open('assets/sample_mcaps.json') as f:
    mcaps = json.load(f)
spy = pd.read_csv('assets/sample_prices.csv')['SPY'].pct_change().dropna()
bl_result = bl_pipeline(rets, spy.values, mcaps,
                        view_dict={'BMA': 0.25, 'LOMA': 0.4},
                        view_confidences=[0.3, 0.5], rf=0.045)
print(bl_result['posterior'])  # retornos a posteriori

# --- HRP ---
hrp_result = hrp_portfolio(rets, linkage_method='ward')
print(hrp_result['weights'])  # pesos HRP
```

---

## Dependencias

| Librería | Requerida | Uso |
|----------|:---------:|-----|
| `numpy` | ✅ | Cómputo vectorizado, álgebra lineal |
| `pandas` | ✅ | CSV I/O, DataFrames |
| `scipy` | ✅ | `optimize` (Markowitz), `cluster.hierarchy` (HRP/NCO), `stats` |

**No requiere** Riskfolio-Lib, PyPortfolioOpt, sklearn, cvxpy ni arch.

Para visualización (dendrogramas, frontera eficiente) se puede usar `matplotlib`
opcionalmente. Ejemplos de plots están en el notebook de referencia.

---

## Referencias Teóricas

- **Markowitz (1952)**: "Portfolio Selection", *Journal of Finance*.
- **Black & Litterman (1992)**: "Global Portfolio Optimization", *Financial Analysts Journal*.
- **Idzorek (2005)**: "A Step-by-Step Guide to the Black-Litterman Model".
- **Lopez de Prado (2016)**: "Building Diversified Portfolios that Outperform Out of Sample" (HRP).
- **De Prado (2019)**: "Nested Clustered Optimization", [SSRN 3469961](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3469961).
- **Pfitzinger & Katzke (2019)**: "NCO with Constraints", [SSRN 4409173](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4409173).
- **Meucci (2006)**: "Beyond Black-Litterman: Views on Non-Normal Markets", [SSRN 1213325](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1213325).
- **Avramov (2004)**: "Bayesian Variable Selection in Portfolio Analysis", [SSRN 3326617](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3326617).

Para profundizar en **ratios de performance** (30+ métricas: Sharpe, Sortino,
VaR, cVaR, Kelly, Rachev, Profit Factor, etc.) y **backtesting** de estrategias:
[`skills/backtesting`](https://github.com/gauss314/skills/tree/main/skills/backtesting).

---

## Notebook de referencia

El contenido teórico y ejemplos numéricos de este skill están basados en:
- `temp/Clase_08_teoria_2025_portafolio.ipynb` — Implementaciones en Python de
  Markowitz, Monte Carlo, NCO (Riskfolio-Lib), Black-Litterman (PyPortfolioOpt).
- `temp/Portafolios 2025 Ucema.pdf` — Marco teórico: MPT, CAPM, Fama-French,
  clustering, NCO, Black-Litterman.

Las implementaciones **flat numpy** en `scripts/` replican los resultados de esos
notebooks sin depender de las librerías mencionadas.
