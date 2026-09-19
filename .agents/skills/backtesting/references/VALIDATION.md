# Suite de Validación — 4 Niveles

El script `validate.py` ejecuta **31 checks** en 4 niveles para asegurar que
todo el framework de backtesting sea matemáticamente correcto,
económicamente coherente y resiliente a casos borde.

## Uso Rápido

```bash
# Suite completa (31 checks)
py scripts/validate.py

# Nivel específico
py scripts/validate.py --nivel 1
```

---

## Level 1 — CLI Modes (14 checks)

Cada comando CLI se invoca con datos reales de mercado y assets built-in.
Verifica: sin crashes, los outputs contienen resultados válidos.

| # | Check | Fuente de datos | Qué verifica |
|---|-------|----------------|--------------|
| 1 | `validate` | `assets/validation_cases.json` | 4 casos sintéticos pasan (constante, normal, drawdown, binomial) |
| 2 | `run SPY` | `assets/sp500_close.csv` (SPY real, 1993-2026) | CAGR ≈ 8.8%, Sharpe ≈ 0.55, MaxDD ≈ -56% |
| 3 | `run built-in` | `assets/sp500_returns.csv` | Ratio computation con CSV de retornos 1980-2025 |
| 4 | `run --benchmark` | momentum + sp500 returns | Benchmark: R², tracking error, payoff summary |
| 5 | `walkforward SPY` | `assets/sp500_close.csv` | 4 splits expanding-window con IS/OOS |
| 6 | `walkforward built-in` | `assets/sp500_returns.csv` | Walk-forward sobre dataset de 45 años |
| 7 | `event` SMA crossover | `assets/sp500_prices.csv` | BacktestEngine genera trades desde OHLCV |
| 8 | `optmpt` multi-asset | `assets/multi_asset_prices.csv` | Markowitz: SPY + QQQ + GLD + TLT + BTC |
| 9 | `optmpt` built-in | `assets/sp500_returns.csv` | Optimización con 1 activo (peso ≈ 1.0) |
| 10 | `marginal` | `assets/sp500_close.csv` | Distribution fitting: Johnson SU best fit |
| 11 | `marginal` built-in | `assets/sp500_returns.csv` | Mismo con 45 años de retornos |
| 12 | `forward project` | `assets/sp500_close.csv` | Fan chart projection con Johnson SU |
| 13 | `forward risk` | `assets/sp500_close.csv` | Forward VaR, cVaR, MaxDD, ruin probability |
| 14 | `forward stress` | `assets/sp500_close.csv` | Parametric shock sobre SPY |

---

## Level 2 — Mathematical Consistency (7 checks)

Cada ratio se testea contra propiedades matemáticas conocidas.

| # | Check | Método | Propiedad |
|---|-------|--------|-----------|
| 15 | **Scale invariance** | Compute all ratios en P y P×1000 | Sharpe, Sortino, MaxDD, CAGR, Kelly, Calmar, Rachev, profit factor, payoff son idénticos |
| 16 | **Serie constante vol** | 252 días a +1%/día | Vol anualizada ≈ 0 |
| 17 | **Serie constante MaxDD** | 252 días a +1%/día | Max drawdown ≈ 0 |
| 18 | **Serie constante Sharpe** | 252 días a +1%/día | Sharpe → ∞ (vol → 0) |
| 19 | **Walk-forward ruido blanco** | N(0, 1%) returns | Sin crash con datos aleatorios; splits generados |
| 20 | **DuPont ROE** | Income + balance sintéticos | `roe_check` (producto de 5 factores) ≈ `roe_direct` (NI/Equity) |
| 21 | **Altman Z** | Income + balance sintéticos | Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E verificado |

---

## Level 3 — Edge Cases (8 checks)

El framework debe manejar entradas degeneradas sin crash.

| # | Input | Comportamiento esperado |
|---|-------|------------------------|
| 22 | 2 filas de datos | Sharpe = NaN, CAGR calculable |
| 23 | 3 filas de datos | Sin crash |
| 24 | Precios negativos | NaN propagado silenciosamente, sin crash |
| 25 | Serie plana (todo 100) | Sharpe = NaN, CAGR = 0 |
| 26 | NaN en serie de precios | NaNs descartados, sin crash |
| 27 | Comisión = 100% | CAGR = -100% (costo destruye todo el capital) |
| 28 | Walk-forward gap = 5000 | 4 splits generados (gap < datos, split 0 skip por IS vacío) |
| 29 | Markowitz con 1 activo | Weight ≈ 1.0 |

---

## Level 4 — Regression (4 checks)

Validación post-fixes para asegurar que nada está roto.

| # | Check | Método |
|---|-------|--------|
| 30 | `pytest test_ratios.py` | Todos los 18 tests unitarios pasan |
| 31 | Markowitz reproducibilidad | Misma seed=42 → mismo portfolio óptimo (verifica RNG aislado) |
| 32 | Parameter sweep | Variación de parámetros produce resultados distintos (estrategia evaluada correctamente) |
| 33 | Monte Carlo search | Combinaciones aleatorias de parámetros producen resultados distintos |

---

## Ejemplo de salida

```
   ▐▛σ σ▜▌     Finance skills
  ▝▜█████▛▘    multi-module suite
   ▘▘   ▝▝

  ▸ Level 1 — CLI Modes (14 checks: CLI execution + metrics)
  ──────────────────────────────────────────────────────
    ✓ validate  · 4/4 synthetic cases pass
    ✓ SPY buy & hold 1993-2026  · CAGR 8.8% · Sharpe 0.55
    ...

  ▸ Level 2 — Mathematical Consistency (7 checks: ratio properties)
  ───────────────────────────────────────────────────────────
    ✓ Scale invariance  · 10 ratios unchanged
    ...

  RESULT: ✓ 31/31 checks passed — 0 failed
```

---

## Mantenimiento

Al agregar una nueva feature o corregir un bug:

1. Agregar un check en el nivel correspondiente de `validate.py`
2. Verificar que pase con `py scripts/validate.py --nivel N`
3. Correr la suite completa para confirmar que no hay regresiones

La estructura de 4 niveles asegura que:
- Los comandos CLI no crashean (**Level 1**)
- La matemática es correcta (**Level 2**)
- Los casos borde se manejan (**Level 3**)
- La funcionalidad existente se preserva (**Level 4**)
