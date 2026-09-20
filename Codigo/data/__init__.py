"""Extractores de datos de mercado."""

# market_data: API principal (stockprices.dev + yfinance)
from .market_data import get_spot, get_quote, get_expirations, get_options_chain

try:
    from .market_data import (
        get_dividend_yield,
        get_risk_free_rate,
        get_risk_free_rate_with_source,
        get_implied_vol_atm,
        calc_implied_vol_atm,
        calc_implied_vol_atm_with_source,
    )
except ImportError:
    def get_dividend_yield(ticker: str) -> float:
        return 0.0

    def get_risk_free_rate() -> float:
        return 0.05

    def get_risk_free_rate_with_source():
        return (0.05, "fallback")

    def get_implied_vol_atm(chain_df, spot: float, expiry: str):
        return None

    def calc_implied_vol_atm(chain_df, spot, expiry, r, div, price_source="mid"):
        return None

    def calc_implied_vol_atm_with_source(chain_df, spot, expiry, r, div, price_source="mid"):
        return None

# nyse: funciones legacy para notebooks
from .nyse import (
    get_stock_price,
    obtener_opciones_yahoo_finance,
    obtener_panel_opciones_nyse,
)

_SENTINEL = object()


def __getattr__(name):
    """Lazy import: byma_market, byma legacy y homebroker se cargan bajo demanda."""
    if name == "byma_market":
        from . import byma_market as mod
        globals()[name] = mod
        return mod
    try:
        from . import byma as _byma_mod
        val = getattr(_byma_mod, name, _SENTINEL)
        if val is not _SENTINEL:
            globals()[name] = val
            return val
    except ImportError:
        pass
    try:
        from . import homebroker as _hb_mod
        val = getattr(_hb_mod, name, _SENTINEL)
        if val is not _SENTINEL:
            globals()[name] = val
            return val
    except ImportError:
        pass
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
