# Finanzas Cuantitativas app (UCEMA / pública)

Streamlit. Pricing de opciones, payoffs y estrategias con market data.

## Páginas

| Página | Descripción |
|--------|-------------|
| **Propiedades de opciones** | Sensibilidad precio vs S, K, T, r, sigma, div |
| **Modelos y Estrategias** | Vanilla, estrategias, Payoff Explorer |
| **Griegas** | Delta, Gamma, Vega, Rho, Theta vs Spot |
| **Market Data** | Ticker, spot, options chain (NYSE) |
| **Market Data + Pricing** | Estrategias con precios de mercado, escenarios S×T |

## Inicio rápido

```bash
pip install -r webapp/requirements.txt
python -m streamlit run webapp/app.py
```

Windows: `webapp\run_webapp.bat`

Abrí http://localhost:8501

## Branches

- **`main`** (esta): versión UCEMA / pública.
- **`mia`** (local, no publicar): features privadas (Superficie IV, IBKR OCR, `VolSurface/`). No mergear `mia` → `main`.

## Requisitos

Incluye `yahooquery` y `requests` (Market Data).

Si hay error `numpy.dtype size changed`: `pip install --upgrade numpy pandas`
