# Placeholder — Estado del proyecto

**Última actualización:** septiembre 2026

---

## Branches

- **`main`**: webapp UCEMA / pública (sin Superficie IV ni IBKR).
- **`mia`**: privada local — Superficie, IBKR, `VolSurface/`, `vol_surface.py`. No pushear / no mergear a `main`.

---

## Estado actual (webapp pública)

- Páginas: Propiedades, Modelos, Griegas, Market Data, Market Data + Pricing.
- Smoke previo: imports, market data AAPL, pricing BS, suite de tests core.
- UX market data: `webapp/ui_format.py` (expiry/strike).

---

## Hecho (core)

- Engine pricing / strategy_pricer / payoffs
- Market data multi-provider
- Webapp Streamlit UCEMA
