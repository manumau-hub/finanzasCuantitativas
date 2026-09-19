# Derivados Financieros - QUANt - UCEMA

Los codigos son de libre uso para los participantes del curso. Pueden proponer mejoras y hacer pull requests.
Pueden forkear y armar sus librerias. Es un ambiente para jugar un poco y trabajar de manera colaborativa.

## Estructura del proyecto

```
finanzasCuantitativas/
├── webapp/           # Aplicación Streamlit (UCEMA)
│   ├── app.py        # Home + Documentación
│   ├── pages/        # Propiedades, Modelos, Griegas, Market Data, Pricing
│   └── requirements.txt
├── Codigo/           # Módulos Python
│   ├── data/         # Extractores (market_data, byma, nyse, homebroker)
│   ├── pricing/      # Modelos (BS, binomial, MC, FD)
│   ├── utils/        # Utilidades (plots, opciones_byma)
│   ├── analytics/    # Vol implicita, payoffs, gregas_bs
│   └── calculadoras/ # GUIs legacy
├── docs/             # Documentación (WEBAPP_TOOL.md, Sphinx)
├── Notebooks/        # Jupyter notebooks del curso
└── legacy/           # Scripts históricos
```

## Uso

Para ejecutar los notebooks, ejecutar Jupyter desde la raíz del proyecto para que los imports `from Codigo.xxx` funcionen correctamente.

## WebApp

Aplicación Streamlit con:

- **Propiedades de opciones** — Sensibilidad precio vs S, K, T, r, sigma, div
- **Modelos y Estrategias** — Vanilla, estrategias, payoffs (digitales, Asian, barrier)
- **Griegas** — Delta, Gamma, Vega, Rho, Theta, etc. vs Spot
- **Market Data** — Ticker, spot, options chain (NYSE)
- **Market Data + Pricing** — Estrategias con precios de mercado, escenarios S×T

Branch **`main`**: versión pública UCEMA. Features privadas (Superficie IV, IBKR) viven solo en branch local **`mia`** — no mergear `mia` → `main`.

**Arranque:**
```bash
pip install -r webapp/requirements.txt
python -m streamlit run webapp/app.py
```

Abre http://localhost:8501

## Documentación API

```bash
pip install -r docs/requirements.txt
cd docs && python -m sphinx -b html . _build
```

Los archivos HTML quedan en `docs/_build/`.
