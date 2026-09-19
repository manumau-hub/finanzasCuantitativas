# Finanzas Cuantitativas app — Documentación técnica completa

Documento de referencia para agentes y desarrolladores. Describe la webapp UCEMA: Propiedades de opciones, Modelos y Estrategias, Griegas, Market Data, Market Data + Pricing de estrategias, y módulos de backend.

---

## 1. Resumen general

**Finanzas Cuantitativas app** es una webapp Streamlit para pricing de opciones y derivados financieros (curso QUANt UCEMA). Incluye:

| Página | Descripción |
|--------|-------------|
| **Propiedades de opciones** | Sensibilidad del precio ante variación de S, K, T, r, sigma o div (BS, Binomial, MC, FD) |
| **Modelos y Estrategias** | Precios vanilla y estrategias; Payoff Explorer (vanilla, estrategias, digitales, Asian, barrier) |
| **Griegas** | Delta, Gamma, Vega, Rho, Theta, DividendRho, StrikeSensitivity, Elasticity vs Spot; definiciones howto |
| **Market Data** | Ticker, precio spot, variación 1d, options chain (NYSE) |
| **Market Data + Pricing de estrategias** | Construir estrategias con precios de mercado; escenarios S×T; r, sigma, div desde mercado |

**Arranque:**

```bash
pip install -r webapp/requirements.txt
python -m streamlit run webapp/app.py
```

---

## 2. Estructura del proyecto

```
finanzasCuantitativas/
├── webapp/
│   ├── app.py                 # Entry point Streamlit (Home + Documentación)
│   ├── _fetch_r.py            # Script subprocess para ^IRX
│   ├── jupyter_server_config.py
│   ├── requirements.txt
│   └── pages/
│       ├── 0_Propiedades_Opciones.py         # Sensibilidad precio vs parámetros
│       ├── 1_Modelos_y_Estrategias.py       # Modelos y Estrategias + Payoff Explorer
│       ├── 2_Griegas.py                     # Griegas vs Spot (BS europeas)
│       ├── 2_Market_Data.py                 # Market Data (ticker, spot, chain)
│       └── 3_Market_Data_Pricing_de_estrategias.py  # Estrategias con precios de mercado
├── Codigo/
│   ├── pricing/              # Modelos de pricing
│   ├── analytics/            # Vol implícita, payoffs, gregas_bs
│   ├── data/                 # market_data, nyse, byma, homebroker
│   ├── utils/                # plots, opciones_byma
│   └── calculadoras/         # GUIs legacy
├── docs/                     # Sphinx, WEBAPP_TOOL.md
└── Notebooks/                # Jupyter del curso
```

---

## 3. Páginas webapp (detalle)

### 3.1 Propiedades de opciones (`0_Propiedades_Opciones.py`)

**Sensibilidad del precio** ante variación de un parámetro (S, K, T, r, sigma, div). Solo opciones europeas vanilla.

**Parámetros:** S, K, T, r, sigma, div, Tipo (C/P).

**Modelo:** Black-Scholes, Binomial, Monte Carlo, Diferencias finitas + Pasos (bin/MC/FD).

**Parámetro a variar:** Spot, Strike, Time to maturity, r, sigma, div, con rango (desde / a) y número de puntos.

**Gráfico:** Precio de la opción vs parámetro variable.

---

### 3.2 Modelos y Estrategias (`1_Modelos_y_Estrategias.py`)

**Parámetros** (una línea): S, K, T, r, sigma, div, Tipo (C/P), Ejercicio (Europea/Americana)

**Playground:**

- **Modo Vanilla**: Pasos (bin/MC), Modelo (Black-Scholes, Binomial, Monte Carlo, Diferencias finitas), botón Calcular
- **Modo Estrategia**: Selector de estrategia, parámetros dinámicos (K1, K2, K3, K4, n1, n2 según estrategia), botón Calcular. Explicación del payoff debajo.

**Estrategias soportadas:** straddle, short_straddle, covered_call, protective_put, strangle, short_strangle, combo, collar, box, bull_call_spread, bear_call_spread, bull_put_spread, bear_put_spread, ratio_spread, call_butterfly, put_butterfly, iron_butterfly, iron_condor, condor.

**Payoff Explorer:** Categoría (Vanilla, Estrategias, Digitales, Asian, Barrier) → Payoff → parámetros (K, K1–K4, Q, B, barrier_hit) → gráfico matplotlib.

**Payoffs:** Call, Put; Bull/Bear Call/Put Spread; Straddle, Strangle, Combo, Collar, Box; Covered Call, Protective Put; Ratio Spread; Call/Put Butterfly, Iron Butterfly, Iron Condor, Condor; Digital Call/Put; Asian Call/Put; Barrier Up-and-In/Out Call.

---

### 3.3 Griegas (`2_Griegas.py`)

**Griegas vs Spot** para opciones europeas vanilla (Black-Scholes analítico).

**Griegas:** Delta, Gamma, Vega, Rho, Theta, DividendRho, StrikeSensitivity, Elasticity.

**Parámetros:** S, K, T, r, sigma, div, Tipo (C/P). Gráfico de cada griega vs Spot (rango configurable).

**Definiciones:** Expander con fórmulas y explicación de cada griega.

---

### 3.4 Market Data (`2_Market_Data.py`)

- Input: ticker + botón **Cargar**
- Muestra: precio spot, variación 1d, fuente (stockprices.dev, yahooquery, etc.)
- Selector de vencimiento + botón **Cargar opciones**
- Tabla pivotada: strike, call bid/ask/last/IV, put bid/ask/last/IV
- Filtros: strike mín/máx

**Windows/OneDrive:** Se redirige stderr a devnull al cargar datos para evitar Errno 22.

**Session state:** `md_ticker`, `md_spot`, `md_quote`, `md_exps`, `md_chain`, `md_source`, `md_error`

---

### 3.5 Market Data + Pricing de estrategias (`3_Market_Data_Pricing_de_estrategias.py`)

**Módulo independiente** (no asume datos de Market Data).

1. **Ticker + Cargar**: spot, exps, chain, div, r, sigma ATM
2. **Stock**: Precio hoy, Precio comprado, Cantidad acciones
3. **Opciones**: Botón **➕ Agregar opción** → legs con:
   - **Expiry, Strike, Tipo** (call/put)
   - **🟢 Long / 🔴 Short** + Cantidad
   - **Bid, Ask, Last, Mid** — selector **Usar** para elegir qué precio usar (mid = (bid+ask)/2)
   - Precio pagado
   - **IV** editable por leg — botones **Calcular IV** (por leg) o **Calcular IV (todas las opciones)** para prellenar (no automático)
   - ×100 lotes
4. **Resumen**: Mercado HOY, Pagado, P&L
5. **Escenarios**:
   - **Grilla**: Columnas (tiempo), Filas (precio S), S desde/hasta. Punto extra cerca del vencimiento para transición suave. Última col = payoff (T=0).
   - **Parámetros**: r (^IRX), div — cada uno con botón **Calcular**. IV por opción (editable en cada leg arriba).
   - **Modelo**: BAW, Binomial, Monte Carlo, Diferencias finitas + parámetros (Pasos, M)
   - **Calcular escenarios**: Solo al pulsar el botón (no automático).
   - **Matriz**: Valor estrategia y P&L con columnas en **fechas** (hoy → expiry). Degradado rojo/verde: más negativo = más rojo, más positivo = más verde.

**r:** subprocess `_fetch_r.py` → ^IRX (Yahoo Chart API). **IV:** `impvolfunc_bs` por leg (precio mid/last). **div:** `get_dividend_yield`.

---

## 4. Módulos backend

### 4.1 `Codigo/pricing/`

**Modelos vanilla:**

| Función | Tipo | Descripción |
|---------|------|-------------|
| `opcion_europea_bs` | Europea | Black-Scholes |
| `opcion_europea_bin` | Europea | Binomial |
| `opcion_europea_bin_c` | Europea | Binomial cerrado |
| `opcion_europea_mc` | Europea | Monte Carlo |
| `opcion_europea_fd` | Europea | Diferencias finitas |
| `opcion_americana_bin` | Americana | Binomial |
| `opcion_americana_fd` | Americana | FD |
| `opcion_americana_bs` | Americana | BAW (Barone-Adesi Whaley) |
| `opcion_americana_mc` | Americana | MC |

**QuantLib:** Versiones `*_ql` si QuantLib está instalado (`_QL_AVAILABLE`).

**Estrategias:** `precio_estrategia_nombre(nombre, S, T, r, sigma, div, **kwargs)` — composición de piernas vanilla. `ESTRATEGIA_PIERNAS` define las piernas por estrategia.

---

### 4.2 `Codigo/analytics/`

**vol_implicita.py:**

- `impvolfunc_bs(tipo, S, K, T, r, precio_mercado, div)` — resuelve σ tal que BS(σ) = precio_mercado (bisect)
- `impvolfunc_bin` — igual para americanas (binomial)

**payoffs.py:** Funciones payoff(S, K, …) para vanilla, estrategias, digitales, Asian, barrier. Aceptan escalares o arrays NumPy.

**gregas_bs.py:** Griegas analíticas Black-Scholes para opciones europeas (equivalente a QuantLib AnalyticEuropeanEngine):

- `delta_bs`, `gamma_bs`, `vega_bs`, `rho_bs`, `theta_bs`
- `theta_per_day_bs`, `dividend_rho_bs`, `strike_sensitivity_bs`, `elasticity_bs`

---

### 4.3 `Codigo/data/`

**market_data.py** (API principal):

| Función | Retorna | Fuentes |
|---------|---------|---------|
| `get_spot(ticker)` | float | stockprices.dev → yahooquery → yahoo-api → yfinance |
| `get_quote(ticker)` | dict | stockprices.dev, yahooquery |
| `get_expirations(ticker)` | list[str] | yahooquery, yfinance |
| `get_options_chain(ticker, exp)` | DataFrame | yahooquery, yfinance |
| `get_dividend_yield(ticker)` | float | yfinance |
| `get_risk_free_rate_with_source()` | (float, str) | ^IRX/^TNX (Chart API, yfinance) |
| `get_implied_vol_atm_with_source` | (float, str) | Columna IV de Yahoo |
| `calc_implied_vol_atm_with_source` | (float, str) | impvolfunc_bs (precio mid o last) |

**nyse.py:** `get_stock_price`, `obtener_opciones_yahoo_finance`, `obtener_panel_opciones_nyse` (legacy).

**byma, homebroker:** Lazy import en `__init__.py`.

---

## 5. Dependencias

| Paquete | Uso |
|---------|-----|
| streamlit | Webapp |
| numpy, scipy | Pricing, payoffs |
| matplotlib | Gráficos payoffs |
| pandas | DataFrames |
| yfinance | Spot, options, div, r (fallback) |
| yahooquery | Spot, options (primario) |
| requests | stockprices.dev, Yahoo Chart API |
| jupyter, jupyterlab | Notebooks embebidos |

---

## 6. Problemas conocidos y soluciones

### 6.1 `numpy.dtype size changed` (incompatibilidad numpy/pandas)

**Causa:** Versiones binarias incompatibles entre numpy y pandas (p. ej. pandas compilado con otra versión de numpy).

**Solución:** `pip install --upgrade numpy pandas`. Si persiste: `pip uninstall numpy pandas -y` y luego `pip install numpy pandas`.

**Nota:** Algunas páginas (Propiedades, Modelos, Griegas) evitan importar pandas al cargar para que la app arranque; Market Data requiere pandas.

### 6.2 `[Errno 22] Invalid argument` (Windows/OneDrive)

**Causa:** Ejecutar la app desde una carpeta sincronizada por OneDrive hace que `print(..., file=sys.stderr)` falle.

**Solución aplicada:** En Market Data y Market Data + Pricing de estrategias, se redirige `sys.stderr` a `os.devnull` durante la carga de datos. En `market_data.py`, `_log()` está deshabilitado (no-op). Si persiste, **mover el proyecto fuera de OneDrive** (ej. `C:\dev\finanzasCuantitativas`).

### 6.3 get_spot falla — "No hay datos"

Orden: stockprices.dev (suele fallar) → yahooquery → yahoo-api → yfinance. yahooquery suele funcionar.

### 6.4 r muestra 5% en vez de ^IRX

Usar subprocess `_fetch_r.py` para obtener r fuera del contexto Streamlit.

### 6.4 IV y sigma: no modificar después del widget

En Market Data + Pricing, la IV por leg es editable solo por el usuario o por los botones **Calcular IV**. No sobrescribir el valor del widget con el leg en cada rerun; solo sincronizar cuando viene de un clic en «Calcular IV».

### 6.6 Sigma "no disponible"

`calc_implied_vol_atm_with_source` necesita bid/ask o lastPrice válidos. Probar `price_source="mid"` o `"last"`.

### 6.7 Mercado HOY incorrecto

Fórmula: `valor_opciones = Σ(qty * 100 * precio_mercado)` donde `precio_mercado` es el que eligió el usuario (bid, ask, last o mid).

### 6.7 Escenarios: columnas con fechas

Las columnas de la matriz de escenarios muestran fechas (dd/mm/yy) en vez de T=0.xxa. Primera col = hoy, última = expiry (T=0, payoff). Se inserta un punto extra entre la anteúltima y la última columna para transición suave al vencimiento. T usa fechas consistentes (sin hora) para evitar errores con BAW.

### 6.9 JupyterLab no carga en Notebooks

JupyterLab debe estar corriendo en otra terminal con `jupyter lab --config=webapp/jupyter_server_config.py`. URL iframe: `http://localhost:8888`.

### 6.10 Diferencias finitas con T muy pequeño

En `american_fd.py` se limita N a 5000 para evitar que la grilla cuelgue con T muy pequeño.

---

## 7. Archivos clave

| Archivo | Rol |
|---------|-----|
| `webapp/app.py` | Entry point |
| `webapp/pages/0_Propiedades_Opciones.py` | Sensibilidad precio vs parámetros |
| `webapp/pages/1_Modelos_y_Estrategias.py` | Modelos y Estrategias + Payoff Explorer |
| `webapp/pages/2_Griegas.py` | Griegas vs Spot (BS europeas) |
| `webapp/pages/2_Market_Data.py` | Market Data |
| `webapp/pages/3_Market_Data_Pricing_de_estrategias.py` | Market Data + Pricing de estrategias |
| `webapp/_fetch_r.py` | Subprocess para r |
| `Codigo/pricing/` | Modelos de pricing |
| `Codigo/analytics/vol_implicita.py` | impvolfunc_bs |
| `Codigo/analytics/gregas_bs.py` | Griegas analíticas BS |
| `Codigo/analytics/payoffs.py` | Payoffs |
| `Codigo/data/market_data.py` | API datos mercado |

---

## 8. Testing rápido

```python
# Pricing
from Codigo.pricing import opcion_europea_bs, precio_estrategia_nombre
print(opcion_europea_bs("C", 100, 100, 1, 0.05, 0.25, 0))
print(precio_estrategia_nombre("straddle", 100, 1, 0.05, 0.25, 0, K=100))

# Market data
from Codigo.data.market_data import get_spot, get_options_chain, calc_implied_vol_atm_with_source
spot = get_spot("AAPL")
chain = get_options_chain("AAPL", None)
out = calc_implied_vol_atm_with_source(chain, spot, "2026-03-06", 0.04, 0.005, "mid")
print("sigma:", out)

# Payoffs
from Codigo.analytics.payoffs import payoff_call, payoff_straddle
import numpy as np
S = np.linspace(80, 120, 50)
print(payoff_straddle(S, K=100)[:5])
```

---

## 9. Referencias

- [Options Profit Calculator](https://www.optionsprofitcalculator.com/)
- [yahooquery](https://pypi.org/project/yahooquery/)
- [yfinance](https://pypi.org/project/yfinance/)
- [QuantLib](https://www.quantlib.org/)
