---
name: backtesting
description: "Academic backtesting framework for quantitative research. ~30 risk and performance ratios, 10 classes of indicators, event-driven engine with 6+ strategies, MPT optimizer, forward-looking simulation with Johnson SU + t-Copula, walk-forward CV, stress testing, fundamental analysis (Altman Z, Piotroski, DuPont). All flat Python + numpy."
license: MIT
---

# Backtesting — Full Backtesting Skill

This skill implements the **full 5-stage backtesting methodology** from the course material:
Data → Research → Metrics → Parameterisation → Validation. It provides:

- **30+ risk/performance ratios** (flat, numpy-vectorized, no classes)
- **10 classes of indicators** following the course taxonomy (trend-following, oscillators, contrarians, flow, combined, discrete counts, seasonality, statistical, referential, fundamental)
- **Event-driven backtesting engine** with 8 built-in strategies
- **Forward-looking simulation** (Johnson SU marginals + t/Gaussian copula)
- **Portfolio theory** (Markowitz efficient frontier, portfolio-of-portfolios)
- **Walk-forward cross-validation** with IS/OOS split + gap
- **Stress testing** with parametric scenario shocks
- **Fundamental analysis** (Altman Z, Piotroski F, DuPont)

All scripts use only `numpy`, `pandas`, and `scipy`. No heavy dependencies.

Part of the [Gauss314 Skills Repository](https://github.com/gauss314/skills).

---

## File Map

```
skills/backtesting/
├── SKILL.md                         ← This file
├── references/
│   ├── BACKTESTING_THEORY.md        ← Marco conceptual: GIGO, trilema, 5 etapas (ES)
│   ├── RATIOS.md                    ← Fórmulas, convención de retornos, advertencias (ES)
│   ├── FEATURES.md                  ← Taxonomía de 10 clases de indicadores con edges (ES)
│   ├── SIMULATIONS.md               ← Pipeline Johnson SU + cópula (ES)
│   ├── VALIDATION.md                ← Suite de validación de 4 niveles (ES)
│   └── OTHER_FEATURES.md            ← Fundamental, Sentimiento, Exógenos (ES)
├── assets/
│   ├── sp500_returns.csv            ← SPY benchmark daily returns (lin + log), 1980-today
│   ├── momentum_sma50_200_returns.csv ← SMA(50)/SMA(200) crossover strategy returns
│   ├── contrarian_bbands_returns.csv  ← Bollinger Band contrarian strategy returns
│   ├── sample_portfolios.json       ← Real investor portfolios (Buffett, Dalio, Ackman, 60/40)
│   ├── defaults.json                ← Default parameters (VaR alpha, windows, etc.)
│   └── validation_cases.json        ← 6 known cases for ratio validation
├── scripts/
│   ├── __init__.py
│   ├── ratios.py                    ← 30+ flat numpy functions for all risk/performance ratios
│   ├── indicators.py                ← 10 classes of technical/statistical/fundamental indicators
│   ├── engine.py                    ← Event-driven BacktestEngine with 8 built-in strategies
│   ├── backtesting.py               ← CLI: run, sweep, walkforward, montecarlo, optmpt, event, validate
│   ├── simulations.py               ← CLI: marginal, copula, run, portfolio, scenarios
│   ├── forward.py                   ← CLI: project, risk, stress, summary
│   ├── distributions.py             ← Fit + KS test for Normal/t/NCt/Laplace/JohnsonSU
│   ├── copulas.py                   ← t/Gaussian/Clayton/Gumbel/Frank copulas + sampling
│   ├── fundamental_ratios.py        ← Income/balance/cashflow metrics, DuPont, Altman Z, Piotroski
│   └── validate.py                  ← 4-level validation: CLI modes, math consistency, edge cases, regression
└── tests/
    └── test_ratios.py               ← 18 pytest tests for core ratios
```

### What each file does

| File | Role | Key Functions / Modes |
|------|------|-----------------------|
| `ratios.py` | The core library. Every ratio is a flat function accepting 1-D arrays. | `sharpe_ratio`, `max_drawdown`, `var_all`, `cvar_all`, `kelly_fraction`, `payoff_ratio`, `profit_factor`, `rachev_a/b/c`, `common_sense_ratio`, `ruin_curve`, `compute_all` |
| `indicators.py` | 10 classes of indicators, covering all types from the course taxonomy. | `rsi`, `adx`, `bbands`, `macd`, `atr`, `cross_indicator`, `range_bound`, `zscore_norm`, `poisson_rate`, `binomial_ratio`, `fourier_terms`, `best_fit_dist` |
| `engine.py` | BacktestEngine class and 8 strategy functions. | `BacktestEngine`, `strategy_sma_crossover`, `strategy_rsi_cross`, `strategy_bbands_contrarian`, `strategy_growth_momentum_combo` |
| `backtesting.py` | Main CLI. Run full backtests, walks, sweeps, optimization. | `run`, `sweep`, `walkforward`, `montecarlo`, `optmpt`, `event`, `validate`, `bench` |
| `simulations.py` | Forward-looking simulation with Johnson SU + copula. | `marginal`, `copula`, `run`, `portfolio`, `scenarios` |
| `forward.py` | Risk projection and stress testing. | `project`, `risk`, `stress`, `summary` |
| `distributions.py` | Distribution fitting and comparison. | `fit`, `best_fit`, `compare_distributions`, `sample` |
| `copulas.py` | Copula fitting and sampling. | `fit_t`, `fit_gaussian`, `sample_t`, `sample_gaussian`, `validate_copula` |
| `fundamental_ratios.py` | Fundamental analysis ratios. | `income_metrics`, `valuation_metrics`, `dupont`, `altman_z`, `piotroski` |
| `validate.py` | 4-level integration testing suite. | 33 checks across CLI, math, edge cases, regression |

---

## Quick Start

### Basic Ratios

```bash
# Compute all 30+ ratios on a CSV of prices
py scripts/backtesting.py run --prices assets/sp500_returns.csv

# Compute with benchmark comparison
py scripts/backtesting.py run --prices assets/momentum_sma50_200_returns.csv --benchmark assets/sp500_returns.csv
```

### Validate (4-level suite)

```bash
# Full validation (33 checks across 4 levels)
py scripts/validate.py

# Single level
py scripts/validate.py --nivel 1
```

Validates CLI modes, mathematical consistency of all ratios, edge case resilience, and post-fix regression. See [`references/VALIDATION.md`](./references/VALIDATION.md) for the detailed breakdown of all 33 checks.

### Event-Driven Backtest

```bash
# Load a CSV with OHLCV data and run SMA crossover
py scripts/backtesting.py event --data my_stock.csv --strategy sma_crossover --fast 50 --slow 200 --commission 0.001
```

### Parameter Sweep

```bash
# 2D sweep over fast/slow MA windows
py scripts/backtesting.py sweep --prices assets/sp500_returns.csv --p1-min 10 --p1-max 100 --p1-step 10
# 2D over 2 parameters
py scripts/backtesting.py sweep --prices assets/sp500_returns.csv --p1-min 10 --p1-max 50 --p1-step 5 --p2-min 25 --p2-max 200 --p2-step 25
```

### Walk-Forward

```bash
py scripts/backtesting.py walkforward --prices assets/sp500_returns.csv --splits 5 --gap 21
```

### Markowitz Optimization

```bash
py scripts/backtesting.py optmpt --assets assets/sp500_returns.csv --iterations 5000
```

### Forward Simulation

```bash
py scripts/simulations.py marginal --returns assets/sp500_returns.csv
py scripts/simulations.py copula --returns assets/sp500_returns.csv --df 4
py scripts/forward.py project --returns assets/sp500_returns.csv --horizon 252 --paths 10000 --drift 0.08
py scripts/forward.py risk --returns assets/sp500_returns.csv --horizon 252 --paths 10000
```

### Portfolio Simulation

```bash
py scripts/simulations.py portfolio --name warren_buffett
py scripts/simulations.py scenarios --name warren_buffett --cagr -0.3,-0.15,0,0.2,0.35,0.5
```

---

## Using Ratios as a Library

```python
from scripts.ratios import *

prices = np.array([100, 105, 102, 110, 108, 115])
r = linear_returns(prices)    # [0.05, -0.0286, 0.0784, -0.0182, 0.0648]
lr = log_returns(prices)      # [0.0488, -0.0290, 0.0755, -0.0183, 0.0628]

sharpe_ratio(r)               # 0.847
max_drawdown(prices)          # -0.0370
kelly_fraction(lr)            # 0.0793
var_all(r, alpha=0.05)        # {'empirical': ..., 'normal': ..., 'johnsonsu': ...}
profit_factor(lr)             # 2.314
payoff_ratio(lr)              # 1.578
rachev_c(lr, alpha=0.05)      # 1.234
common_sense_ratio(lr)        # 2.856
```

## Using the Engine

```python
from scripts.engine import BacktestEngine

eng = BacktestEngine(initial_capital=1.0, commission=0.001, slippage=0.0005)
eng.load_data(df_ohlcv)
result = eng.run(strategy='sma_crossover', strategy_params={'fast': 50, 'slow': 200})

print(result['metrics']['sharpe_ratio'])     # 0.847
print(result['trades'])
print(result['metrics'])
```

---

## Dependencies

| Library | Required | Used for |
|---------|:--------:|----------|
| `numpy` | ✅ | Vectorised computation, arrays, cumprod |
| `pandas` | ✅ | CSV I/O, rolling operations, DataFrames |
| `scipy.stats` | ✅ | Distribution fitting, KS test, copulas |
| `statsmodels` | Optional | STL decomposition in indicators.py (Class 5) |

To run the full validation suite (`py scripts/validate.py`) you also need `pytest` for the Level 4 regression check.

No `arch`, `quantlib`, `sklearn` required.

---

## See Also

- [Gauss314 Skills Repository](https://github.com/gauss314/skills) — other skills for financial data
- `references/BACKTESTING_THEORY.md` — marco conceptual del backtesting (ES)
- `references/RATIOS.md` — fórmulas, convención de retornos, advertencias (ES)
- `references/FEATURES.md` — taxonomía de 10 clases de indicadores con edges (ES)
- `references/SIMULATIONS.md` — pipeline de Johnson SU + cópula (ES)
- `references/VALIDATION.md` — suite de validación de 4 niveles (ES)
- `references/OTHER_FEATURES.md` — fundamental, sentimiento, exógenos (ES)
