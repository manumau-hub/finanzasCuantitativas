# UCEMA QUANT (pública)

Streamlit. Pricing de opciones, payoffs y estrategias con market data. Solo español.

## Páginas

| Página | Descripción |
|--------|-------------|
| **UCEMA QUANT** | Home + documentación |
| **Propiedades de opciones** | Clase 1 y 2 — Sensibilidad precio vs S, K, T, r, sigma, div |
| **Payoffs y Estrategias** | Clase 1 y 2 — Vanilla, estrategias, Payoff Explorer |
| **Market Data** | Clase 1 y 2 — Ticker, spot, options chain (NYSE) |
| **Griegas** | Clases 3 y 4 — Delta, Gamma, Vega, Rho, Theta vs Spot |
| **Market Data Pricing** | Clases 3 y 4 — Estrategias con precios de mercado, escenarios S×T |
| **Notebooks** | JupyterLab |

## Cómo levantar la app

Desde la **raíz del repo**:

```bash
pip install -r webapp/requirements.txt
python -m streamlit run webapp/UCEMA_QUANT.py
```

**Windows:** `webapp\run_webapp.bat`

Abrí [http://localhost:8501](http://localhost:8501)

## Branches

- **`main`** (esta): versión UCEMA / pública.
- **`mia`** (local, no publicar): features privadas (Superficie IV, IBKR OCR). No mergear `mia` → `main`.
