# Finanzas Cuantitativas app (branch `mia` — privada)

Streamlit. Pricing de opciones, payoffs, volatilidad implícita, estrategias, **Superficie IV** e **IBKR OCR**.

> Branch privada local. **No mergear a `main` ni pushear** a origin.

## Páginas

| Página | Descripción |
|--------|-------------|
| **Propiedades de opciones** | Sensibilidad precio vs S, K, T, r, sigma, div |
| **Modelos y Estrategias** | Vanilla, estrategias, Payoff Explorer |
| **Griegas** | Delta, Gamma, Vega, Rho, Theta vs Spot |
| **Market Data** | Ticker, spot, options chain (NYSE) |
| **Superficie de volatilidad** | IV vs Delta × TTM |
| **Market Data + Pricing** | Estrategias con precios de mercado, escenarios S×T |
| **Estrategias IBKR** | OCR capturas → estrategia |

Notebooks: `pages/_5_Notebooks.py` (oculto; quitar `_` para mostrar).

## Inicio

```bash
pip install -r webapp/requirements.txt
python -m streamlit run webapp/app.py
```

## Branches

- `mia` (esta): todo, incluido Superficie + IBKR + `VolSurface/` + `vol_surface.py`
- `main` (UCEMA / pública): sin ese código privado
