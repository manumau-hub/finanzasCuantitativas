# Placeholder — Estado del proyecto

**Última actualización:** septiembre 2026

---

## Estado actual (webapp)

- Smoke OK: imports, `get_spot`/`get_expirations` (AAPL), pricing BS, **88 tests** passed.
- Páginas **ocultas** (prefix `_`): Notebooks, Estrategias IBKR. Ver `webapp/README.md`.
- `requirements.txt` incluye `yahooquery`, `requests`, `plotly`; pin `numpy<2` relajado (entorno actual usa numpy 2.x).

---

## Hecho

- Engine vol_surface migrado desde VolSurface
- Tests: pricing, strategy_pricer, payoffs, vol_surface (suite completa OK en smoke reciente)
- UX market data: formato estable de expiry/strike (`webapp/ui_format.py`)
