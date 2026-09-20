# -*- coding: utf-8 -*-
"""
BYMA / mercado argentino — spot, quote, opciones e histórico.

Fuentes (en orden de preferencia para opciones):
  1. data912.com ``/live/arg_options`` — panel con bid/ask/last (~450 series)
  2. open.bymadata.com.ar ``/options`` — API oficial pública (a menudo incompleta
     fuera de rueda)

Spot / quote: data912 ``/live/arg_stocks`` + ``/live/arg_cedears``, con
fallback a paneles BYMA e histórico.
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd
import requests
import urllib3

from Codigo.utils.opciones_byma import (
    conversor_ticker,
    fecha_expiracion,
    mes_nombre_a_numero,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_BYMA = "https://open.bymadata.com.ar/vanoms-be-core/rest/api/bymadata/free"
BASE_912 = "https://data912.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
}

PANELS = {
    "leading-equity": "leading-equity",
    "cedears": "cedears",
    "options": "options",
}

# Raíz de ticker de opción → subyacente (complementa conversor_ticker)
_ROOT_TO_UNDER = {
    "AGR": "AGRO", "ALU": "ALUA", "BBA": "BBAR", "BHI": "BHIP", "BMA": "BMA",
    "BOL": "BOLT", "BYM": "BYMA", "CAR": "CARC", "CEC": "CECO2", "CEP": "CEPU",
    "COM": "COME", "CRE": "CRES", "EDN": "EDN", "GFG": "GGAL", "LOM": "LOMA",
    "GVA": "VALO", "MIR": "MIRG", "MOR": "MORI", "PAM": "PAMP", "SUP": "SUPV",
    "TEC": "TECO2", "TGN": "TGNO4", "TGS": "TGSU2", "TRA": "TRAN", "TXA": "TXAR",
    "YPF": "YPFD", "TSL": "TSLA", "MEL": "MELI", "GOD": "GOLD", "APL": "AAPL",
    "MET": "METR",
}

_OPT_RE = re.compile(
    r"^([A-Z]{2,4})([CV])(\d+(?:\.\d+)?)[.]?([A-Z]{1,2})$"
)


def _post_byma(path: str, payload: dict | None = None) -> Any:
    r = requests.post(
        f"{BASE_BYMA}/{path}", headers=HEADERS, json=payload or {}, timeout=30, verify=False,
    )
    r.raise_for_status()
    return r.json()


def _get_byma(path: str, params: dict) -> Any:
    r = requests.get(
        f"{BASE_BYMA}/{path}", headers=HEADERS, params=params, timeout=30, verify=False,
    )
    r.raise_for_status()
    return r.json()


def _get_912(path: str) -> Any:
    r = requests.get(f"{BASE_912}{path}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def _panel_items(raw: Any) -> list[dict]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        data = raw.get("data")
        if isinstance(data, list):
            return data
    return []


def fetch_panel(panel: str, *, t1: bool = True, fetch_all: bool = True) -> list[dict]:
    if panel not in PANELS:
        raise ValueError(f"Panel inválido: {panel}")
    payload: dict[str, Any] = {"page_size": 5000 if fetch_all else 200}
    if t1:
        payload["T1"] = True
    return _panel_items(_post_byma(PANELS[panel], payload))


def _norm_ticker(ticker: str) -> str:
    return (ticker or "").strip().upper().replace(".BA", "")


def _roots_for_underlying(ticker: str) -> set[str]:
    """Raíces de opción que corresponden al subyacente (ej. GGAL → {GFG, GGAL})."""
    t = _norm_ticker(ticker)
    roots = {t, t[:3], t[:4]}
    for root, und in _ROOT_TO_UNDER.items():
        if und == t:
            roots.add(root)
    # conversor_ticker es root→und; buscar raíces cuyo mapeo caiga en t
    for root in list(roots):
        if conversor_ticker(root) == t:
            roots.add(root)
    return {r for r in roots if r}


def _parse_option_symbol(symbol: str) -> Optional[dict]:
    """
    Parsea ticker BYMA/data912: GFGC4600OC, ALUC700.OC, CEPC2036DI.
    Retorna root, underlying, type, strike, expiration (YYYY-MM-DD).
    """
    s = (symbol or "").strip().upper().replace(" ", "")
    m = _OPT_RE.match(s)
    if not m:
        return None
    root, cv, strike_s, mes = m.group(1), m.group(2), m.group(3), m.group(4)
    und = _ROOT_TO_UNDER.get(root) or conversor_ticker(root)
    typ = "call" if cv == "C" else "put"
    mes_num = mes_nombre_a_numero(mes)
    if mes_num == 0 and len(mes) == 1:
        mes_num = mes_nombre_a_numero(mes)
    try:
        exp = fecha_expiracion(mes_num)
        exp_s = exp.isoformat()
    except Exception:
        exp_s = None
    if mes_num == 0:
        exp_s = None
    return {
        "root": root,
        "underlying": und,
        "type": typ,
        "strike": float(strike_s),
        "expiration": exp_s,
        "month_code": mes,
    }


def _pick_row(items: list[dict], ticker: str) -> Optional[dict]:
    t = _norm_ticker(ticker)
    matches = [it for it in items if str(it.get("symbol", "")).upper() == t]
    if not matches:
        return None
    for it in matches:
        if str(it.get("settlementType")) == "2":
            return it
    return matches[0]


def _last_price(row: dict) -> Optional[float]:
    for key in ("trade", "closingPrice", "settlementPrice", "vwap", "previousClosingPrice", "c"):
        v = row.get(key)
        try:
            f = float(v)
            if f > 0:
                return f
        except (TypeError, ValueError):
            continue
    return None


def _spot_data912(ticker: str) -> Optional[float]:
    t = _norm_ticker(ticker)
    for path in ("/live/arg_stocks", "/live/arg_cedears"):
        try:
            items = _get_912(path)
        except Exception:
            continue
        if not isinstance(items, list):
            continue
        for it in items:
            if str(it.get("symbol", "")).upper() == t:
                for key in ("c", "px_bid", "px_ask"):
                    try:
                        v = float(it.get(key) or 0)
                        if v > 0:
                            get_spot.last_source = f"data912{path}"
                            return v
                    except (TypeError, ValueError):
                        continue
    return None


def get_spot(ticker: str) -> float:
    """Spot: data912 → paneles BYMA → último cierre histórico."""
    t = _norm_ticker(ticker)
    px = _spot_data912(t)
    if px is not None:
        return px
    for panel in ("leading-equity", "cedears"):
        try:
            row = _pick_row(fetch_panel(panel), t)
        except Exception:
            row = None
        if row is None:
            continue
        px = _last_price(row)
        if px is not None:
            get_spot.last_source = f"BYMA/{panel}"
            return px
    hist = get_history(t, days=30)
    if hist is not None and not hist.empty:
        get_spot.last_source = "BYMA/historico"
        return float(hist["Precio"].iloc[-1])
    get_spot.last_source = None
    raise ValueError(
        f"BYMA/data912: sin precio para {t} (ej. GGAL, YPFD, PAMP, AAPL CEDEAR)"
    )


get_spot.last_source = None


def get_quote(ticker: str) -> dict:
    t = _norm_ticker(ticker)
    for path in ("/live/arg_stocks", "/live/arg_cedears"):
        try:
            items = _get_912(path)
        except Exception:
            continue
        if not isinstance(items, list):
            continue
        for it in items:
            if str(it.get("symbol", "")).upper() != t:
                continue
            last = None
            for key in ("c", "px_bid", "px_ask"):
                try:
                    v = float(it.get(key) or 0)
                    if v > 0:
                        last = v
                        break
                except (TypeError, ValueError):
                    continue
            pct = it.get("pct_change")
            try:
                pct = float(pct) if pct is not None else None
            except (TypeError, ValueError):
                pct = None
            return {
                "last": last,
                "change": None,
                "changePercent": pct,
                "name": t,
                "source": f"data912{path}",
                "currency": "ARS",
                "bid": it.get("px_bid"),
                "ask": it.get("px_ask"),
                "volume": it.get("v"),
            }
    try:
        last = get_spot(t)
        return {
            "last": last, "change": None, "changePercent": None,
            "name": t, "source": get_spot.last_source, "currency": "ARS",
        }
    except Exception:
        return {"last": None, "change": None, "changePercent": None, "name": t, "source": None}


def _options_from_data912(ticker: str) -> list[dict]:
    """Panel data912 filtrado por subyacente, normalizado a schema interno."""
    t = _norm_ticker(ticker)
    roots = _roots_for_underlying(t)
    try:
        raw = _get_912("/live/arg_options")
    except Exception:
        return []
    if not isinstance(raw, list):
        return []
    out = []
    for it in raw:
        sym = str(it.get("symbol", ""))
        parsed = _parse_option_symbol(sym)
        if parsed is None:
            continue
        if parsed["underlying"] != t and parsed["root"] not in roots:
            continue
        # forzar underlying canónico
        if conversor_ticker(parsed["root"]) == t or parsed["underlying"] == t:
            pass
        elif parsed["root"] not in roots:
            continue
        bid = float(it.get("px_bid") or 0) or None
        ask = float(it.get("px_ask") or 0) or None
        last = float(it.get("c") or 0) or None
        out.append({
            "symbol": sym,
            "underlyingSymbol": t,
            "optionType": "CALL" if parsed["type"] == "call" else "PUT",
            "strike": parsed["strike"],
            "maturityDate": parsed["expiration"],
            "bidPrice": bid,
            "offerPrice": ask,
            "trade": last,
            "closingPrice": last,
            "volume": float(it.get("v") or 0),
            "openInterest": float(it.get("q_op") or 0),
            "_source": "data912",
        })
    return out


def _options_from_byma(ticker: str) -> list[dict]:
    t = _norm_ticker(ticker)
    try:
        items = fetch_panel("options", t1=False, fetch_all=True)
    except Exception:
        return []
    rows = [it for it in items if str(it.get("underlyingSymbol", "")).upper() == t]
    for r in rows:
        if not r.get("strike"):
            parsed = _parse_option_symbol(str(r.get("symbol", "")))
            if parsed:
                r["strike"] = parsed["strike"]
                if not r.get("maturityDate") and parsed.get("expiration"):
                    r["maturityDate"] = parsed["expiration"]
        r["_source"] = "BYMA"
    return rows


LAST_OPTIONS_SOURCE: Optional[str] = None


def _options_raw(ticker: str) -> list[dict]:
    """Preferir data912 (panel rico); si vacío, BYMA open API."""
    global LAST_OPTIONS_SOURCE
    rows = _options_from_data912(ticker)
    if rows:
        LAST_OPTIONS_SOURCE = "data912/arg_options"
        return rows
    rows = _options_from_byma(ticker)
    LAST_OPTIONS_SOURCE = "BYMA/options" if rows else None
    return rows


def get_options_source() -> Optional[str]:
    return LAST_OPTIONS_SOURCE


def get_expirations(ticker: str) -> list[str]:
    dates = sorted({
        str(it.get("maturityDate"))[:10]
        for it in _options_raw(ticker)
        if it.get("maturityDate")
    })
    return dates


def get_options_chain(ticker: str, expiration: Optional[str] = None) -> pd.DataFrame:
    """Cadena normalizada (columnas compatibles con Market Data NYSE)."""
    t = _norm_ticker(ticker)
    rows = _options_raw(t)
    src = LAST_OPTIONS_SOURCE or "—"
    if expiration:
        exp = str(expiration)[:10]
        rows = [r for r in rows if str(r.get("maturityDate", ""))[:10] == exp]
    if not rows:
        raise ValueError(
            f"Sin opciones para {t}"
            + (f" @ {expiration}" if expiration else "")
            + ". Fuentes: data912 /live/arg_options y BYMA open API. "
            "Probá GGAL, YPFD, PAMP, ALUA, CEPU."
        )

    spot = None
    try:
        spot = get_spot(t)
    except Exception:
        pass

    out = []
    for r in rows:
        opt = str(r.get("optionType", "")).upper()
        typ = "call" if opt.startswith("C") else ("put" if opt.startswith("P") else None)
        if typ is None:
            # infer from symbol
            parsed = _parse_option_symbol(str(r.get("symbol", "")))
            typ = parsed["type"] if parsed else None
        if typ is None:
            continue
        strike = r.get("strike")
        try:
            strike = float(strike) if strike is not None else None
        except (TypeError, ValueError):
            strike = None
        if strike is None:
            parsed = _parse_option_symbol(str(r.get("symbol", "")))
            strike = parsed["strike"] if parsed else None
        if strike is None:
            continue
        last = _last_price(r)
        bid = float(r.get("bidPrice") or 0) or None
        ask = float(r.get("offerPrice") or 0) or None
        out.append({
            "contractSymbol": r.get("symbol"),
            "strike": float(strike),
            "type": typ,
            "expiration": str(r.get("maturityDate", "") or "")[:10] or None,
            "bid": bid,
            "ask": ask,
            "lastPrice": last,
            "volume": float(r.get("volume") or r.get("tradeVolume") or 0),
            "openInterest": float(r.get("openInterest") or 0),
            "impliedVolatility": float("nan"),
            "Spot": spot,
            "Ticker": t,
            "source": r.get("_source") or src,
        })
    df = pd.DataFrame(out)
    if df.empty:
        raise ValueError(f"No se pudieron parsear strikes de opciones para {t}")
    get_options_chain.last_source = src
    return df


get_options_chain.last_source = None


def get_history(ticker: str, days: int = 365) -> Optional[pd.DataFrame]:
    """Histórico OHLCV diario → DataFrame index datetime, columna Precio."""
    t = _norm_ticker(ticker)
    # data912 historical stocks
    try:
        raw = _get_912(f"/historical/stocks/{t}")
        if isinstance(raw, list) and raw:
            df = pd.DataFrame(raw)
            if "date" in df.columns and "c" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.set_index("date").sort_index()
                out = df[["c"]].rename(columns={"c": "Precio"}).tail(days)
                if not out.empty:
                    return out
    except Exception:
        pass
    symbol = f"{t} 24HS"
    hasta = int(time.time())
    desde = hasta - days * 86400
    try:
        raw = _get_byma(
            "chart/historical-series/history",
            {"symbol": symbol, "resolution": "D", "from": desde, "to": hasta},
        )
    except Exception:
        return None
    if not isinstance(raw, dict) or raw.get("s") != "ok":
        return None
    ts = raw.get("t") or []
    closes = raw.get("c") or []
    if not ts or not closes:
        return None
    idx = [datetime.fromtimestamp(int(x), tz=timezone.utc).date() for x in ts]
    return pd.DataFrame({"Precio": [float(c) for c in closes]}, index=pd.to_datetime(idx))
