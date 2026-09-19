# -*- coding: utf-8 -*-
"""
Market Data - Precios spot y opciones (NYSE / US equities).

Proveedores (en orden de prioridad):
  Spot/Quote:   stockprices.dev  ->  yahooquery  ->  Yahoo v8 API  ->  yfinance
  Options:      yahooquery (primario)  ->  yfinance (fallback)
"""
from __future__ import annotations

import sys
from typing import Optional, Tuple

import pandas as pd
import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
_TIMEOUT = 10


# ═══════════════════════════════════════════════════════════════════════════
# SPOT PRICE — multiple providers with automatic fallback
# ═══════════════════════════════════════════════════════════════════════════

def _spot_stockprices(ticker: str) -> float:
    """stockprices.dev — sin auth, sin rate-limit."""
    for endpoint in ("stocks", "etfs"):
        url = f"https://stockprices.dev/api/{endpoint}/{ticker}"
        try:
            r = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            if r.status_code != 200:
                continue
            data = r.json()
            price = data.get("Price")
            if price is not None:
                return float(price)
        except Exception:
            continue
    raise ValueError("stockprices.dev: sin datos")


def _spot_yahooquery(ticker: str) -> float:
    """yahooquery — backend directo de Yahoo, más estable que yfinance."""
    from yahooquery import Ticker as YQTicker
    tk = YQTicker(ticker)
    p = tk.price
    if isinstance(p, dict) and ticker in p and isinstance(p[ticker], dict):
        val = p[ticker].get("regularMarketPrice")
        if val is not None:
            return float(val)
    raise ValueError("yahooquery: sin datos")


def _spot_yahoo_api(ticker: str) -> float:
    """Yahoo Finance v8 chart API — HTTP directo."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {"range": "5d", "interval": "1d"}
    try:
        r = requests.get(url, headers=_HEADERS, params=params, timeout=_TIMEOUT)
        if r.status_code != 200:
            raise ValueError(f"status {r.status_code}")
        data = r.json()
        closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        valid = [c for c in closes if c is not None]
        if valid:
            return float(valid[-1])
    except (KeyError, IndexError, TypeError):
        pass
    raise ValueError("yahoo-api: sin datos")


def _spot_yfinance(ticker: str) -> float:
    """yfinance — último recurso."""
    import yfinance as yf
    tk = yf.Ticker(ticker)
    for period in ("5d", "1mo"):
        try:
            hist = tk.history(period=period)
            if not hist.empty:
                return float(hist["Close"].iloc[-1])
        except Exception:
            continue
    raise ValueError("yfinance: sin datos")


# Orden: HTTP puro primero (sin cache), luego libs (yahooquery, yfinance)
# Evita Errno 22 en Windows/OneDrive cuando cache/archivos fallan
_SPOT_PROVIDERS = [
    ("stockprices.dev", _spot_stockprices),
    ("yahoo-api", _spot_yahoo_api),  # HTTP directo, sin cache
    ("yahooquery", _spot_yahooquery),
    ("yfinance", _spot_yfinance),
]


def get_spot(ticker: str) -> float:
    """
    Precio spot actual.  Prueba proveedores en orden hasta que uno funcione.
    Setea get_spot.last_source con el nombre de la fuente usada.
    """
    errs: list[str] = []
    for name, fn in _SPOT_PROVIDERS:
        try:
            price = fn(ticker)
            get_spot.last_source = name
            return price
        except Exception as e:
            errs.append(f"[{name}] {e}")
    get_spot.last_source = None
    raise ValueError(f"Sin precio para {ticker}: {' | '.join(errs)}")

get_spot.last_source = None


# ═══════════════════════════════════════════════════════════════════════════
# QUOTE — precio + variación + nombre
# ═══════════════════════════════════════════════════════════════════════════

def get_quote(ticker: str) -> dict:
    """
    Cotización completa: last, change, changePercent, name, bid, ask, volume.
    Primero stockprices.dev, luego yahooquery.
    """
    # stockprices.dev
    for endpoint in ("stocks", "etfs"):
        url = f"https://stockprices.dev/api/{endpoint}/{ticker}"
        try:
            r = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            if r.status_code != 200:
                continue
            d = r.json()
            if d.get("Price") is not None:
                return {
                    "last": d["Price"],
                    "change": d.get("ChangeAmount"),
                    "changePercent": d.get("ChangePercentage"),
                    "name": d.get("Name"),
                    "source": "stockprices.dev",
                }
        except Exception:
            continue

    # yahooquery
    try:
        from yahooquery import Ticker as YQTicker
        tk = YQTicker(ticker)
        p = tk.price
        if isinstance(p, dict) and ticker in p and isinstance(p[ticker], dict):
            info = p[ticker]
            rmp = info.get("regularMarketPrice")
            if rmp is not None:
                pct = info.get("regularMarketChangePercent")
                return {
                    "last": rmp,
                    "change": info.get("regularMarketChange"),
                    "changePercent": round(pct * 100, 2) if pct else None,
                    "name": info.get("shortName"),
                    "source": "yahooquery",
                }
    except Exception:
        pass

    return {"last": None, "change": None, "changePercent": None, "name": None, "source": None}


# ═══════════════════════════════════════════════════════════════════════════
# OPTIONS — expirations + chain  (yahooquery primary, yfinance fallback)
# ═══════════════════════════════════════════════════════════════════════════

def get_expirations(ticker: str) -> list[str]:
    """Fechas de vencimiento disponibles. yahooquery -> yfinance fallback."""
    # yahooquery
    try:
        from yahooquery import Ticker as YQTicker
        tk = YQTicker(ticker)
        chain = tk.option_chain
        if hasattr(chain, "index"):
            exps = chain.index.get_level_values("expiration").unique()
            return sorted([ts.strftime("%Y-%m-%d") for ts in exps])
    except Exception:
        pass

    # yfinance fallback
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        exps = tk.options
        return list(exps) if exps else []
    except Exception:
        pass

    return []


def get_options_chain(ticker: str, expiration: Optional[str] = None) -> pd.DataFrame:
    """
    Cadena de opciones completa para un vencimiento.

    Retorna DataFrame con columnas: strike, bid, ask, lastPrice,
    impliedVolatility, volume, openInterest, type, expiration, Spot, Ticker.
    """
    # yahooquery
    try:
        df = _chain_yahooquery(ticker, expiration)
        if df is not None and not df.empty:
            return df
    except Exception:
        pass

    # yfinance fallback
    return _chain_yfinance(ticker, expiration)


def get_options_chain_yfinance(
    ticker: str,
    max_expirations: Optional[int] = None,
) -> pd.DataFrame:
    """
    Cadena de opciones usando solo yfinance (evita yahooquery).
    Útil cuando yahooquery causa problemas de serialización (ej. Streamlit).
    max_expirations: límite de vencimientos (None = todos).
    """
    return _chain_yfinance(ticker, expiration=None, max_expirations=max_expirations)


def _chain_yahooquery(ticker: str, expiration: Optional[str]) -> pd.DataFrame | None:
    from yahooquery import Ticker as YQTicker
    tk = YQTicker(ticker)
    chain = tk.option_chain
    if not hasattr(chain, "index"):
        return None

    df = chain.reset_index()
    df = df.rename(columns={"optionType": "type"})
    df["type"] = df["type"].map({"calls": "call", "puts": "put"}).fillna(df["type"])

    if "expiration" in df.columns:
        df["expiration"] = pd.to_datetime(df["expiration"]).dt.strftime("%Y-%m-%d")

    if expiration:
        df = df[df["expiration"] == expiration]
        if df.empty:
            return None

    spot = get_spot(ticker)
    df["Spot"] = spot
    df["Ticker"] = ticker
    return df


def _chain_yfinance(
    ticker: str,
    expiration: Optional[str],
    max_expirations: Optional[int] = None,
) -> pd.DataFrame:
    import yfinance as yf
    tk = yf.Ticker(ticker)
    exps = tk.options
    if not exps:
        raise ValueError(f"No hay opciones para {ticker} (Yahoo puede estar limitando)")

    if expiration and expiration in exps:
        exps_to_fetch = [expiration]
    else:
        exps_to_fetch = list(exps)
        if max_expirations is not None:
            exps_to_fetch = exps_to_fetch[:max_expirations]
    panels = []
    spot = get_spot(ticker)
    for exp in exps_to_fetch:
        chain = tk.option_chain(exp)
        calls = chain.calls.copy()
        puts = chain.puts.copy()
        calls["type"] = "call"
        puts["type"] = "put"
        calls["expiration"] = exp
        puts["expiration"] = exp
        calls["Spot"] = spot
        puts["Spot"] = spot
        panels.append(pd.concat([calls, puts], ignore_index=True))
    panel = pd.concat(panels, ignore_index=True)
    panel["Ticker"] = ticker
    return panel


# ═══════════════════════════════════════════════════════════════════════════
# PARÁMETROS DE PRICING — div, r, sigma implícita
# ═══════════════════════════════════════════════════════════════════════════

def get_dividend_yield(ticker: str) -> float:
    """
    Tasa de dividendos anual (decimal). Yahoo Finance: dividendYield en info.
    Retorna 0.0 si no hay datos.
    """
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        info = tk.info
        if isinstance(info, dict):
            dy = info.get("dividendYield") or info.get("yield")
            if dy is not None:
                v = float(dy)
                if v > 1:  # viene en % (ej. 2.5)
                    return v / 100.0
                return v
    except Exception:
        pass
    return 0.0


def get_risk_free_rate() -> float:
    """Tasa libre de riesgo (decimal). Ver get_risk_free_rate_with_source para fuente."""
    val, _ = get_risk_free_rate_with_source()
    return val


def get_risk_free_rate_with_source() -> Tuple[float, str]:
    """
    Tasa libre de riesgo (decimal) y fuente. ^IRX (13-week T-bill) o ^TNX (10y).
    Yahoo devuelve el valor en porcentaje (ej. 3.59 para 3.59%), se divide por 100.
    Retorna (valor_decimal, "fuente").
    """
    def _from_chart_api(symbol: str) -> Optional[Tuple[float, str]]:
        try:
            from urllib.parse import quote
            url = "https://query1.finance.yahoo.com/v8/finance/chart/" + quote(symbol, safe="")
            r = requests.get(url, headers=_HEADERS, params={"range": "5d", "interval": "1d"}, timeout=15)
            if r.status_code != 200:
                return None
            data = r.json()
            res = data.get("chart", {}).get("result")
            if not res:
                return None
            closes = res[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
            valid = [c for c in closes if c is not None]
            if valid:
                last = float(valid[-1])
                dec = last / 100.0 if last > 1 else last
                return (dec, symbol)
        except Exception:
            pass
        return None

    def _from_yf(symbol: str) -> Optional[Tuple[float, str]]:
        try:
            import yfinance as yf
            tk = yf.Ticker(symbol)
            hist = tk.history(period="5d", auto_adjust=False)
            if not hist.empty and "Close" in hist.columns:
                last = float(hist["Close"].iloc[-1])
                if 0 < last < 100:
                    return (last / 100.0, symbol)
                if 0 < last <= 1:
                    return (last, symbol)
            info = tk.info
            if isinstance(info, dict):
                v = info.get("regularMarketPrice") or info.get("previousClose")
                if v is not None:
                    val = float(v)
                    return (val / 100.0 if val > 1 else val, symbol)
        except Exception:
            pass
        return None

    for sym in ("^IRX", "^TNX"):
        out = _from_chart_api(sym)
        if out is not None:
            return out

    for sym in ("^IRX", "^TNX", "IRX", "TNX"):
        out = _from_yf(sym)
        if out is not None:
            return out

    return (0.05, "fallback")


def get_implied_vol_atm(chain_df: pd.DataFrame, spot: float, expiry: str) -> Optional[float]:
    """Vol implícita ATM (Yahoo). Ver get_implied_vol_atm_with_source para (valor, fuente)."""
    out = get_implied_vol_atm_with_source(chain_df, spot, expiry)
    return out[0] if out else None


def get_implied_vol_atm_with_source(chain_df: pd.DataFrame, spot: float, expiry: str) -> Optional[Tuple[float, str]]:
    """
    Volatilidad implícita ATM desde columna Yahoo. Retorna (valor, "fuente") o None.
    Fallbacks: strike/strikePrice, call→put si IV NaN, varios strikes ordenados por distancia.
    """
    try:
        if chain_df is None or chain_df.empty:
            return None
        exp_col = "expiration" if "expiration" in chain_df.columns else "expirationDate"
        iv_col = next((c for c in ["impliedVolatility", "implied volatility", "implied_volatility"] if c in chain_df.columns), None)
        if iv_col is None:
            return None
        if exp_col not in chain_df.columns:
            return None
        type_col = next((c for c in ["type", "optionType"] if c in chain_df.columns), None)
        if type_col is None:
            return None
        strike_col = next((c for c in ["strike", "strikePrice"] if c in chain_df.columns), None)
        if strike_col is None:
            return None
        exp_str = str(expiry)[:10]
        for opt_type in ("call", "put"):
            sub = chain_df[
                (chain_df[exp_col].astype(str).str[:10] == exp_str) &
                (chain_df[type_col].astype(str).str.lower().str[:4] == opt_type[:4])
            ]
            if sub.empty:
                continue
            sub = sub.copy()
            sub["_dist"] = (sub[strike_col].astype(float) - spot).abs()
            sub = sub.sort_values("_dist")
            for _, row in sub.iterrows():
                iv = row.get(iv_col)
                if pd.notna(iv) and float(iv) > 0:
                    v = float(iv)
                    if v > 1:
                        v = v / 100.0
                    return (v, "IV Yahoo ATM")
    except Exception:
        pass
    return None


def calc_implied_vol_atm(
    chain_df: pd.DataFrame,
    spot: float,
    expiry: str,
    r: float,
    div: float,
    price_source: str = "mid",
) -> Optional[float]:
    """
    Calcula vol implícita ATM usando impvolfunc_bs (Black-Scholes).
    price_source: "mid" = (bid+ask)/2, "last" = lastPrice.
    """
    out = calc_implied_vol_atm_with_source(chain_df, spot, expiry, r, div, price_source)
    return out[0] if out else None


def calc_implied_vol_atm_with_source(
    chain_df: pd.DataFrame,
    spot: float,
    expiry: str,
    r: float,
    div: float,
    price_source: str = "mid",
) -> Optional[Tuple[float, str]]:
    """
    Calcula volatilidad implícita ATM usando impvolfunc_bs y retorna (valor, fuente).
    price_source: "mid" = (bid+ask)/2, "last" = lastPrice.
    """
    from datetime import datetime
    try:
        from Codigo.analytics.vol_implicita import impvolfunc_bs
    except ImportError:
        return None

    try:
        if chain_df is None or chain_df.empty:
            return None
        exp_col = "expiration" if "expiration" in chain_df.columns else "expirationDate"
        if exp_col not in chain_df.columns:
            return None
        type_col = next((c for c in ["type", "optionType"] if c in chain_df.columns), None)
        if type_col is None:
            return None
        strike_col = next((c for c in ["strike", "strikePrice"] if c in chain_df.columns), None)
        if strike_col is None:
            return None

        exp_str = str(expiry)[:10]
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
        now = datetime.now()
        delta = exp_date - now.replace(hour=0, minute=0, second=0, microsecond=0)
        T = max(delta.days, 1) / 365.0
        if T <= 0:
            return None

        for opt_type in ("call", "put"):
            tipo = "C" if opt_type == "call" else "P"
            sub = chain_df[
                (chain_df[exp_col].astype(str).str[:10] == exp_str) &
                (chain_df[type_col].astype(str).str.lower().str[:4] == opt_type[:4])
            ]
            if sub.empty:
                continue
            sub = sub.copy()
            sub["_dist"] = (sub[strike_col].astype(float) - spot).abs()
            sub = sub.sort_values("_dist")

            for _, row in sub.iterrows():
                K = float(row[strike_col])
                if price_source == "mid":
                    bid = row.get("bid")
                    ask = row.get("ask")
                    if pd.notna(bid) and pd.notna(ask) and float(bid) > 0 and float(ask) > 0:
                        precio_mercado = (float(bid) + float(ask)) / 2.0
                    else:
                        continue
                else:
                    last = row.get("lastPrice") or row.get("last") or row.get("Last")
                    if pd.notna(last) and float(last) > 0:
                        precio_mercado = float(last)
                    else:
                        continue

                try:
                    iv = impvolfunc_bs(tipo, spot, K, T, r, precio_mercado, div)
                    if iv is not None and 0 < iv < 5:
                        src = f"BS ATM ({price_source})"
                        return (iv, src)
                except Exception:
                    continue
    except Exception:
        pass
    return None
