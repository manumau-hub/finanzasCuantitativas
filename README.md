# Derivados Financieros - QUANt 2024 - UCEMA

Los codigos son de libre uso para los participantes del curso. Pueden proponer mejoras y hacer pull requests.
Pueden forkear y armar sus librerias. Es un ambiente para jugar un poco y trabajar de manera colaborativa.

## Estructura del proyecto

```
finanzasCuantitativas/
├── webapp/           # Aplicación Streamlit
│   ├── app.py        # Home + Documentación
│   ├── pages/        # Propiedades, Modelos, Griegas, Market Data, Superficie IV, IBKR, Notebooks
│   └── requirements.txt
├── Codigo/           # Módulos Python
│   ├── data/         # Extractores (market_data, byma, nyse, homebroker)
│   ├── pricing/      # Modelos (BS, binomial, MC, FD)
│   ├── utils/        # Utilidades (plots, opciones_byma)
│   ├── analytics/    # Vol implicita, payoffs, gregas_bs
│   └── calculadoras/ # GUIs legacy
├── docs/             # Documentación (WEBAPP_TOOL.md, Sphinx)
├── Notebooks/        # Jupyter notebooks del curso
│   ├── curso/        # Clases (Clase3, Clase4, Clase5, yFinance, WebScraping)
│   ├── temas/        # Por tema (montecarlo, gregas, volatilidad, etc.)
│   ├── ejercicios/   # Ejercicios (Put Call parity, Arbitrajes, etc.)
│   └── codigo/       # Notebooks de demo/ejemplos de código
└── legacy/           # Scripts históricos sin relación con el curso
```

## Uso

Para ejecutar los notebooks, ejecutar Jupyter desde la raíz del proyecto para que los imports `from Codigo.xxx` funcionen correctamente.

## WebApp

Aplicación Streamlit con:

- **Propiedades de opciones** — Sensibilidad precio vs S, K, T, r, sigma, div
- **Modelos y Estrategias** — Vanilla, estrategias, payoffs (digitales, Asian, barrier)
- **Griegas** — Delta, Gamma, Vega, Rho, Theta, etc. vs Spot
- **Market Data** — Ticker, spot, options chain (NYSE)
- **Superficie de volatilidad** — IV vs Delta × TTM
- **Market Data + Pricing** — Estrategias con precios de mercado, escenarios S×T

(Notebooks e IBKR OCR están ocultos en el menú; ver `webapp/README.md` para reactivarlos.)

**Terminal — Streamlit:**
```bash
pip install -r webapp/requirements.txt
python -m streamlit run webapp/app.py
```

Abre http://localhost:8501


## Documentación API

La documentación se genera con Sphinx:

```bash
pip install -r docs/requirements.txt
cd docs && python -m sphinx -b html . _build
```

Los archivos HTML quedan en `docs/_build/`. Abrir `index.html` en un navegador.




