# Migración VolSurface → finanzasCuantitativas

Análisis de qué código de `VolSurface` se puede migrar para la webapp de finanzas cuantitativas.

---

## 1. Estructura del proyecto VolSurface

| Archivo | Propósito | Migrable |
|---------|-----------|----------|
| `volatility_surface.py` | `gaussian_smooth`, `cubic_spline`, `from_vendor` | **Parcial** |
| `implied_vol_calculator.py` | IV desde precios (bisection, newton, jakel, brent, etc.) | **Parcial** |
| `DataBaseAccess.py` | SQL Server, Vendor, Pandora (IvyDB) | **No** |
| `pricingmodel.py` | QuantLib, LR, CRR, Trinomial, BS | **No** (ya tenés modelos propios) |
| `axioma_vol_surface.py` | Wrapper que usa DB + vol_surface | **No** |
| `Dividend_calculation_methods.py` | Dividendos desde DB | **No** |
| `CacheAccess.py` | Cache de superficies | **No** |

---

## 2. Qué SÍ se puede migrar

### 2.1 `gaussian_smooth` (volatility_surface.py)

**Qué hace:** Suavizado Vega-weighted de la superficie en espacio (Delta, TTM). Usa kernel gaussiano en log(TTM), Delta y Call/Put.

**Input esperado:**
```
Date, TTM (días), YearFraction, CallPut, Strike, ImpliedVol, OptionPrice, Spot, Vega, Delta
```

**Output:** DataFrame con TTM, Delta, CallPut, ImpliedVol, Dispersion en puntos estándar (30, 60, 91... días; deltas 0.2–0.8).

**Adaptación necesaria:**
- Agregar `from scipy.stats import norm` (falta en el original).
- Crear función `chain_to_raw_iv_data(chain_df, spot, r, div)` que convierta la options chain de Yahoo a ese formato:
  - TTM y YearFraction desde `expiration`
  - ImpliedVol: usar columna Yahoo o `impvolfunc_bs` si falta
  - Delta, Vega: `delta_bs`, `vega_bs` de `gregas_bs`
  - OptionPrice: mid (bid+ask)/2 o lastPrice

**Dependencias:** `numpy`, `pandas`, `scipy`, `joblib` (ya usados en finanzasCuantitativas).

---

### 2.2 `cubic_spline` (volatility_surface.py)

**Qué hace:** Interpolación cúbica por TTM en espacio Delta–IV.

**Nota:** El código tiene un bug (línea 86): `df_output[df_output['TTM']==ttm]['ImpliedVol'] = ...` no modifica el DataFrame (asignación sobre vista). Hay que corregirlo al migrar.

---

### 2.3 `generate_volatility_surface_point`

**Qué hace:** Interpola IV en un punto (tipo, días, delta) usando el mismo kernel gaussiano.

**Uso:** Obtener IV para un strike/vencimiento arbitrario a partir de la superficie.

---

### 2.4 Lógica de root-finders (implied_vol_calculator.py)

**Qué hace:** Bisection, brentq, toms748, ridder para IV desde precio de mercado.

**Situación:** finanzasCuantitativas ya tiene `impvolfunc_bs` (bisect) y `calc_implied_vol_atm_with_source`. Para europeas BS alcanza. Los métodos extra (newton, brent, etc.) solo aportan si usás americanas o modelos más complejos.

**Recomendación:** No migrar por ahora. Si más adelante necesitás americanas con dividendos, se puede extraer solo `bisection_method` y adaptarlo a `opcion_americana_bin`.

---

## 3. Qué NO se puede migrar (o no conviene)

| Componente | Motivo |
|------------|--------|
| `DataBaseAccess`, Vendor, Pandora | SQL Server, IvyDB; finanzasCuantitativas usa Yahoo Finance |
| `ImpliedVolatilityCalculator` completo | Depende de ZC curve, PricingModel, PricingArguments |
| `pricingmodel.py` | QuantLib/LR/CRR; ya tenés `opcion_europea_bs`, binomial, etc. |
| `from_vendor` | Depende de `pullVolatilitySurfaceOfSecurityID` en DB |
| `axioma_vol_surface` | Orquesta DB + dividendos + vol surface |
| `Dividend_calculation_methods` | Pensado para dividendos discretos desde DB |

---

## 4. Plan de migración sugerido

### Paso 1: Adaptador chain → raw IV

En `Codigo/analytics/` o `Codigo/data/`:

```python
def chain_to_raw_iv_data(chain_df, spot, r, div, price_source="mid"):
    """
    Convierte options chain (Yahoo) a formato para gaussian_smooth.
    Retorna DataFrame con: Date, TTM, YearFraction, CallPut, Strike, ImpliedVol,
    OptionPrice, Spot, Vega, Delta, ExerciseStyle.
    """
```

- Recorrer chain por strike/expiration
- TTM = días hasta vencimiento
- IV: columna `impliedVolatility` o `impvolfunc_bs` si falta
- Delta, Vega: `delta_bs`, `vega_bs` con esa IV

### Paso 2: Copiar y adaptar `gaussian_smooth`

- Crear `Codigo/analytics/vol_surface.py`
- Copiar clase `log_normal_vol_surface` (base) y `gaussian_smooth`
- Agregar `from scipy.stats import norm`
- Ajustar `ttms` y `year_fractions` si hace falta (hoy están hardcodeados)
- Opcional: `cubic_spline` con el fix del bug

### Paso 3: Página webapp

- `webapp/pages/4_Superficie_Volatilidad.py`
- Ticker → cargar chains para varios vencimientos (como en Market Data)
- Unir chains → `chain_to_raw_iv_data` → `gaussian_smooth().generate_volatility_surface()`
- Gráfico: heatmap o 3D (IV vs Strike/Moneyness × TTM)

---

## 5. Diferencias de formato

| VolSurface (Vendor/DB) | finanzasCuantitativas (Yahoo) |
|------------------------|------------------------------|
| SecurityID, pullOptionPricesTable | ticker, get_options_chain |
| ZC curve (Days, Rate) | r fijo o _fetch_r.py |
| Dividend yield desde DB | get_dividend_yield(ticker) |
| TTM en días, Delta en decimal | Mismo, pero hay que calcular Delta |
| IV ya calculada (DBImpVol) o desde precios | impliedVolatility o impvolfunc_bs |

---

## 6. Resumen

| Componente | Acción |
|------------|--------|
| `gaussian_smooth` | **Migrar** con adaptador chain→raw_iv |
| `cubic_spline` | **Migrar** opcional (corregir bug) |
| `generate_volatility_surface_point` | **Migrar** (útil para IV en punto arbitrario) |
| `chain_to_raw_iv_data` | **Crear** (adaptador Yahoo → formato VolSurface) |
| DataBaseAccess, ImpliedVolCalculator, pricingmodel | **No migrar** |

Con esto tenés la lógica de superficie de volatilidad (suavizado e interpolación) reutilizando código probado de VolSurface, alimentada por datos de Yahoo en lugar de base de datos.

---

## 7. Migración completada (2025-03)

- **`Codigo/analytics/vol_surface.py`**: `log_normal_vol_surface`, `gaussian_smooth`, `chain_to_raw_iv_data`
- **`Codigo/analytics/__init__.py`**: exporta `gaussian_smooth`, `chain_to_raw_iv_data`
- **`Codigo/tests/test_vol_surface.py`**: tests unitarios

**Uso:**
```python
from Codigo.analytics import gaussian_smooth, chain_to_raw_iv_data
import pandas as pd
# chain_df = get_options_chain(ticker)  # o concatenar varios vencimientos
raw = chain_to_raw_iv_data(chain_df, spot, r, div)
surf = gaussian_smooth().generate_volatility_surface(raw)
# surf: DataFrame con TTM, Delta, CallPut, ImpliedVol, Dispersion
```
