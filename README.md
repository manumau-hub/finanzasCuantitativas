# Derivados Financieros - QUANt - UCEMA

Los codigos son de libre uso para los participantes del curso. Pueden proponer mejoras y hacer pull requests.
Pueden forkear y armar sus librerias. Es un ambiente para jugar un poco y trabajar de manera colaborativa.

## Estructura del proyecto

```
finanzasCuantitativas/
├── webapp/           # Aplicación Streamlit (UCEMA QUANT)
│   ├── UCEMA_QUANT.py  # Home + Documentación
│   ├── pages/        # Propiedades, Payoffs, Market Data, Griegas, Pricing, Notebooks
│   └── requirements.txt
├── Codigo/           # Módulos Python
│   ├── data/         # Extractores (market_data, byma, nyse, homebroker)
│   ├── pricing/      # Modelos (BS, binomial, MC, FD)
│   ├── utils/        # Utilidades (plots, opciones_byma)
│   ├── analytics/    # Vol implicita, payoffs, gregas_bs
│   └── calculadoras/ # GUIs legacy
├── docs/             # Documentación (WEBAPP_TOOL.md, Sphinx)
└── Notebooks/
    └── ejes/         # Notebooks del curso por eje temático
```

## Uso

Para ejecutar los notebooks, ejecutar Jupyter desde la raíz del proyecto para que los imports `from Codigo.xxx` funcionen correctamente.

## Cómo levantar la app (UCEMA QUANT)

Desde la **raíz del repo** (`finanzasCuantitativas/`):

**1. Dependencias** (una vez):
```bash
pip install -r webapp/requirements.txt
```

**2. Arrancar Streamlit:**
```bash
python -m streamlit run webapp/UCEMA_QUANT.py
```

**Windows (alternativa):** doble clic o ejecutar `webapp\run_webapp.bat`.

**3. Abrir en el navegador:** [http://localhost:8501](http://localhost:8501)

El menú lateral tiene las páginas del curso (Propiedades, Payoffs, Market Data, Griegas, Market Data Pricing, Notebooks).

## WebApp — páginas

- **Propiedades de opciones** — Clase 1–2 · Eje 2 — Sensibilidad Call/Put (BS / BAW)
- **Payoffs y Estrategias** — Clase 1–2 · Ejes 1 y 3 — Vanilla, estrategias, payoffs
- **Market Data** — Clase 1–2 · Eje 4 — Ticker, spot, options chain
- **Modelos de Pricing** — Comparar BS, binomial, MC, FD, BAW…
- **Griegas** — Clases 3–4 — Delta, Gamma, Vega, Rho, Theta, etc. vs Spot
- **Market Data Pricing** — Clases 3–4 · Ejes 3 y 4 — Estrategias con precios de mercado, escenarios S×T
- **Notebooks** — JupyterLab · `Notebooks/ejes/`

## Documentación API

```bash
pip install -r docs/requirements.txt
cd docs && python -m sphinx -b html . _build
```

Los archivos HTML quedan en `docs/_build/`.
