# -*- coding: utf-8 -*-
"""Market Data Pricing — construcción de estrategias + escenarios."""
import io
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
_WEBAPP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, str(_WEBAPP_DIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import norm

from i18n import _
from ui_format import (
    fmt_expiries,
    fmt_expiry,
    fmt_strike_label,
    nearest_strike_index,
    norm_strike,
    norm_strikes,
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
    div[class*="block-container"], div[class*="BlockContainer"] { max-width: none !important; }
</style>
""", unsafe_allow_html=True)

st.title(_("mdp.title"))

with st.expander(f"📖 {_('mdp.how_to_use')}", expanded=False):
    st.markdown(f"""
    1. {_("mdp.help_1")}
    2. {_("mdp.help_2")}
    3. {_("mdp.help_3")}
    4. {_("mdp.help_4")}
    5. {_("mdp.help_5")}
    6. {_("mdp.help_6")}
    7. {_("mdp.help_7")}
    8. {_("mdp.help_8")}
    """)
st.info(
    "📚 **Teoría:** `Notebooks/ejes/03_estrategias/` + "
    "`Notebooks/ejes/04_market_data_i/`. Esta página combina ambos con precios reales."
)

# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════

def _bs_greeks(tipo: str, S: float, K: float, T: float, r: float,
               sigma: float, div: float = 0.0) -> dict:
    """Griegas Black-Scholes analíticas. tipo='C'|'P'."""
    if T <= 1e-6 or sigma <= 0 or S <= 0 or K <= 0:
        d = 1.0 if (tipo == "C" and S >= K) or (tipo == "P" and S <= K) else 0.0
        return {"delta": d * (1 if tipo == "C" else -1), "gamma": 0.0, "vega": 0.0, "theta": 0.0}
    d1 = (np.log(S / K) + (r - div + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    ef = np.exp(-div * T)
    er = np.exp(-r * T)
    if tipo == "C":
        delta = ef * norm.cdf(d1)
        theta = (
            -S * ef * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            - r * K * er * norm.cdf(d2)
            + div * S * ef * norm.cdf(d1)
        ) / 365
    else:
        delta = -ef * norm.cdf(-d1)
        theta = (
            -S * ef * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            + r * K * er * norm.cdf(-d2)
            - div * S * ef * norm.cdf(-d1)
        ) / 365
    gamma = ef * norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega  = S * ef * norm.pdf(d1) * np.sqrt(T) / 100  # per 1 % change in vol
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta}


def _detect_strategy(legs: list, stock_qty: int) -> str:
    if not legs:
        return ""
    calls = [l for l in legs if l.get("type") == "call"]
    puts  = [l for l in legs if l.get("type") == "put"]
    lc = [l for l in calls if int(l.get("qty", 0)) > 0]
    sc = [l for l in calls if int(l.get("qty", 0)) < 0]
    lp = [l for l in puts  if int(l.get("qty", 0)) > 0]
    sp = [l for l in puts  if int(l.get("qty", 0)) < 0]
    n  = len(legs)
    same_exp = len({str(l.get("expiry", ""))[:10] for l in legs}) == 1

    if stock_qty > 0 and n == 1:
        if sc: return "📋 Covered Call"
        if lp: return "🛡️ Protective Put"

    if n == 1:
        q = int(legs[0].get("qty", 0)); t = legs[0].get("type")
        if t == "call": return "📈 Long Call" if q > 0 else "📉 Short Call"
        if t == "put":  return "📉 Long Put"  if q > 0 else "📈 Short Put"

    if n == 2 and same_exp:
        if len(lc) == 1 and len(sc) == 1:
            Kl, Ks = lc[0].get("strike", 0), sc[0].get("strike", 0)
            return "🐂 Bull Call Spread" if Kl < Ks else "🐻 Bear Call Spread"
        if len(lp) == 1 and len(sp) == 1:
            Kl, Ks = lp[0].get("strike", 0), sp[0].get("strike", 0)
            return "🐻 Bear Put Spread" if Kl > Ks else "🐂 Bull Put Spread"
        if len(lc) == 1 and len(lp) == 1:
            Kc, Kp = lc[0].get("strike", 0), lp[0].get("strike", 0)
            return "🔀 Long Straddle" if abs(Kc - Kp) < 0.01 else "🔀 Long Strangle"
        if len(sc) == 1 and len(sp) == 1:
            Kc, Kp = sc[0].get("strike", 0), sp[0].get("strike", 0)
            return "🔀 Short Straddle" if abs(Kc - Kp) < 0.01 else "🔀 Short Strangle"

    if n == 2 and not same_exp:
        if len(lc) == 1 and len(sc) == 1: return "📅 Call Calendar Spread"
        if len(lp) == 1 and len(sp) == 1: return "📅 Put Calendar Spread"

    if n == 3 and same_exp:
        if (len(lc) == 1 and len(sc) == 2) or (len(lc) == 2 and len(sc) == 1):
            return "🦋 Call Butterfly"
        if (len(lp) == 1 and len(sp) == 2) or (len(lp) == 2 and len(sp) == 1):
            return "🦋 Put Butterfly"

    if n == 4 and same_exp:
        if len(lc) == 1 and len(sc) == 1 and len(lp) == 1 and len(sp) == 1:
            Ksc = sc[0].get("strike", 0); Ksp = sp[0].get("strike", 0)
            Klc = lc[0].get("strike", 0); Klp = lp[0].get("strike", 0)
            if Klc > Ksc: return "🦅 Iron Condor"
            return "🦋 Iron Butterfly"

    return _("mdp.custom_strategy", n=n)


def _find_breakevens(S_vals: np.ndarray, pnl: np.ndarray) -> list:
    bes = []
    for i in range(len(pnl) - 1):
        if pnl[i] * pnl[i + 1] < 0:
            x = S_vals[i] - pnl[i] * (S_vals[i + 1] - S_vals[i]) / (pnl[i + 1] - pnl[i])
            bes.append(round(float(x), 2))
    return bes


# ════════════════════════════════════════════════════════════════════════════
# CARGAR TICKER
# ════════════════════════════════════════════════════════════════════════════
col_tick, col_btn = st.columns([4, 1])
with col_tick:
    ticker = st.text_input(_("md.ticker"), value=st.session_state.get("md_ticker", "AAPL"),
                           key="mdp_ticker").strip().upper()
with col_btn:
    st.write(""); st.write("")
    cargar = st.button(_("md.load"), type="primary", key="mdp_cargar")

if cargar and ticker:
    for k in ["md_spot", "md_quote", "md_exps", "md_error", "md_chain",
              "md_div", "md_r", "md_sigma"]:
        st.session_state.pop(k, None)
    st.session_state["md_ticker"] = ticker
    from Codigo.data.market_data import get_spot, get_quote, get_expirations, get_options_chain
    try:
        from Codigo.data.market_data import get_dividend_yield, get_risk_free_rate, get_implied_vol_atm
    except ImportError:
        get_dividend_yield  = lambda t: 0.0
        get_risk_free_rate  = lambda: 0.05
        get_implied_vol_atm = lambda df, s, e: None
    _orig_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass
    try:
        with st.spinner(_("mdp.loading", ticker=ticker)):
            try:
                spot = get_spot(ticker)
                st.session_state["md_spot"] = spot
                exps = fmt_expiries(get_expirations(ticker))
                st.session_state["md_exps"] = exps
                div = get_dividend_yield(ticker)
                st.session_state["md_div"] = round(div, 4)
                r_pct = get_risk_free_rate()
                st.session_state["md_r"] = round(r_pct, 4)
                if exps:
                    chain_df = get_options_chain(ticker, None)
                    if chain_df is not None and not chain_df.empty:
                        if "expiration" in chain_df.columns:
                            chain_df = chain_df.copy()
                            chain_df["expiration"] = chain_df["expiration"].map(fmt_expiry)
                        if "strike" in chain_df.columns:
                            chain_df["strike"] = chain_df["strike"].map(norm_strike)
                    st.session_state["md_chain"] = chain_df
                    sigma_atm = get_implied_vol_atm(chain_df, spot, exps[-1])
                    if sigma_atm is not None:
                        st.session_state["md_sigma"] = round(sigma_atm, 4)
            except Exception as e:
                st.session_state["md_error"] = str(e)
    finally:
        try:
            if sys.stderr != _orig_stderr:
                sys.stderr.close()
            sys.stderr = _orig_stderr
        except Exception:
            pass
    st.rerun()

if "md_error" in st.session_state:
    st.error(st.session_state["md_error"])
    st.stop()

spot          = st.session_state.get("md_spot", 0.0)
exps          = fmt_expiries(st.session_state.get("md_exps", []))
loaded_ticker = st.session_state.get("md_ticker", ticker or "")
chain_df      = st.session_state.get("md_chain")

LOTES = 100  # opciones sobre 100 acciones

# ── Helpers chain (definidos aquí para usarlos en Sugerencias y en Legs) ─────
def _strikes_for_expiry(expiry: str) -> list:
    if chain_df is None or chain_df.empty or not expiry:
        return []
    exp_col = "expiration" if "expiration" in chain_df.columns else "expirationDate"
    if exp_col not in chain_df.columns:
        return []
    sub = chain_df[chain_df[exp_col].astype(str).str[:10] == fmt_expiry(expiry)]
    if "strike" not in sub.columns:
        return []
    return norm_strikes(sub["strike"].tolist())


def _bid_ask_last_from_chain(strike: float, opt_type: str, expiry: str):
    if chain_df is None or chain_df.empty:
        return None, None, None
    exp_col = "expiration" if "expiration" in chain_df.columns else "expirationDate"
    exp_s = fmt_expiry(expiry)
    k = norm_strike(strike)
    match = chain_df[
        (chain_df["type"] == opt_type) &
        (chain_df[exp_col].astype(str).str[:10] == exp_s)
    ]
    if match.empty or "strike" not in match.columns:
        return None, None, None
    # Match tolerante por cercanía (evita fallos float)
    dists = (match["strike"].astype(float) - k).abs()
    row = match.loc[dists.idxmin()]
    if float(dists.min()) > 1e-4:
        return None, None, None
    bid  = float(row["bid"])  if "bid"  in row and pd.notna(row["bid"])  and row["bid"]  >= 0 else None
    ask  = float(row["ask"])  if "ask"  in row and pd.notna(row["ask"])  and row["ask"]  >= 0 else None
    last = row.get("lastPrice") or row.get("last") or row.get("Last")
    last = float(last) if last is not None and pd.notna(last) and float(last) >= 0 else None
    return bid, ask, last

# ════════════════════════════════════════════════════════════════════════════
# SUGERENCIAS DE ESTRATEGIAS
# ════════════════════════════════════════════════════════════════════════════

_STRATEGY_CATALOG = {
    "📈 Direccionales alcistas": {
        "Long Call": {
            "desc": "Compra un call ATM. Ganancia ilimitada si sube, pérdida limitada a la prima.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": atm, "qty": 1, "expiry": exp},
            ],
        },
        "Bull Call Spread": {
            "desc": "Long call ATM + Short call OTM. Costo reducido, ganancia limitada al spread.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": atm,    "qty":  1, "expiry": exp},
                {"type": "call", "strike": otm_c1, "qty": -1, "expiry": exp},
            ],
        },
        "Bull Put Spread": {
            "desc": "Short put OTM + Long put más OTM. Crédito neto, ganancia si el activo sube o queda igual.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "put", "strike": otm_p1, "qty": -1, "expiry": exp},
                {"type": "put", "strike": otm_p2, "qty":  1, "expiry": exp},
            ],
        },
        "Covered Call": {
            "desc": "Stock + Short call OTM. Ingreso de prima, limita la suba. Requiere acciones.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": otm_c1, "qty": -1, "expiry": exp},
            ],
            "note": "⚠️ Recordá poner cantidad de acciones en 'Stock'.",
        },
    },
    "📉 Direccionales bajistas": {
        "Long Put": {
            "desc": "Compra un put ATM. Ganancia si el activo baja, pérdida limitada a la prima.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "put", "strike": atm, "qty": 1, "expiry": exp},
            ],
        },
        "Bear Put Spread": {
            "desc": "Long put ATM + Short put OTM. Costo reducido, ganancia limitada al spread.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "put", "strike": atm,    "qty":  1, "expiry": exp},
                {"type": "put", "strike": otm_p1, "qty": -1, "expiry": exp},
            ],
        },
        "Bear Call Spread": {
            "desc": "Short call OTM + Long call más OTM. Crédito neto, ganancia si el activo baja.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": otm_c1, "qty": -1, "expiry": exp},
                {"type": "call", "strike": otm_c2, "qty":  1, "expiry": exp},
            ],
        },
        "Protective Put": {
            "desc": "Stock + Long put ATM. Seguro contra caídas. Requiere acciones.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "put", "strike": atm, "qty": 1, "expiry": exp},
            ],
            "note": "⚠️ Recordá poner cantidad de acciones en 'Stock'.",
        },
    },
    "🔀 Neutras / Volatilidad": {
        "Long Straddle": {
            "desc": "Long call ATM + Long put ATM. Gana si el activo se mueve mucho en cualquier dirección.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": atm, "qty": 1, "expiry": exp},
                {"type": "put",  "strike": atm, "qty": 1, "expiry": exp},
            ],
        },
        "Short Straddle": {
            "desc": "Short call ATM + Short put ATM. Gana si el activo queda cerca del strike.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": atm, "qty": -1, "expiry": exp},
                {"type": "put",  "strike": atm, "qty": -1, "expiry": exp},
            ],
        },
        "Long Strangle": {
            "desc": "Long call OTM + Long put OTM. Más barato que straddle, necesita mayor movimiento.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": otm_c1, "qty": 1, "expiry": exp},
                {"type": "put",  "strike": otm_p1, "qty": 1, "expiry": exp},
            ],
        },
        "Short Strangle": {
            "desc": "Short call OTM + Short put OTM. Ingreso de prima, riesgo ilimitado en ambas puntas.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": otm_c1, "qty": -1, "expiry": exp},
                {"type": "put",  "strike": otm_p1, "qty": -1, "expiry": exp},
            ],
        },
    },
    "🦋 Complejas": {
        "Long Call Butterfly": {
            "desc": "Long 1 call ATM-spread, Short 2 calls ATM, Long 1 call ATM+spread. Gana si el activo queda en ATM.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": otm_p1, "qty":  1, "expiry": exp},
                {"type": "call", "strike": atm,    "qty": -2, "expiry": exp},
                {"type": "call", "strike": otm_c1, "qty":  1, "expiry": exp},
            ],
        },
        "Iron Condor": {
            "desc": "Short put OTM1 + Long put OTM2 + Short call OTM1 + Long call OTM2. Rango de ganancia entre los shorts.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "put",  "strike": otm_p2, "qty":  1, "expiry": exp},
                {"type": "put",  "strike": otm_p1, "qty": -1, "expiry": exp},
                {"type": "call", "strike": otm_c1, "qty": -1, "expiry": exp},
                {"type": "call", "strike": otm_c2, "qty":  1, "expiry": exp},
            ],
        },
        "Iron Butterfly": {
            "desc": "Long put OTM + Short put ATM + Short call ATM + Long call OTM. Versión comprimida del condor.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "put",  "strike": otm_p1, "qty":  1, "expiry": exp},
                {"type": "put",  "strike": atm,    "qty": -1, "expiry": exp},
                {"type": "call", "strike": atm,    "qty": -1, "expiry": exp},
                {"type": "call", "strike": otm_c1, "qty":  1, "expiry": exp},
            ],
        },
        "Call Calendar Spread": {
            "desc": "Short call vto cercano + Long call vto lejano. Gana con el paso del tiempo.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "call", "strike": atm, "qty": -1, "expiry": exp},
            ],
            "two_expiry": True,
        },
        "Put Calendar Spread": {
            "desc": "Short put vto cercano + Long put vto lejano. Gana con el paso del tiempo.",
            "legs": lambda atm, otm_c1, otm_c2, otm_p1, otm_p2, exp: [
                {"type": "put", "strike": atm, "qty": -1, "expiry": exp},
            ],
            "two_expiry": True,
        },
    },
}

def _closest_strike(strikes: list, target: float) -> float:
    if not strikes:
        return norm_strike(target)
    return norm_strike(min(strikes, key=lambda x: abs(float(x) - target)))

def _build_strategy_legs(strategy_name: str, spot: float, strikes: list,
                          exp_near: str, exp_far: str, spread_pct: float) -> list:
    """Construye legs para la estrategia elegida con los strikes más cercanos disponibles."""
    sp = spread_pct / 100.0
    atm     = _closest_strike(strikes, spot)
    otm_c1  = _closest_strike(strikes, spot * (1 + sp))
    otm_c2  = _closest_strike(strikes, spot * (1 + sp * 2))
    otm_p1  = _closest_strike(strikes, spot * (1 - sp))
    otm_p2  = _closest_strike(strikes, spot * (1 - sp * 2))

    for cat in _STRATEGY_CATALOG.values():
        if strategy_name in cat:
            template = cat[strategy_name]
            is_calendar = template.get("two_expiry", False)
            if is_calendar:
                short_leg = template["legs"](atm, otm_c1, otm_c2, otm_p1, otm_p2, exp_near)
                opt_type = short_leg[0]["type"]
                long_leg = [{"type": opt_type, "strike": atm, "qty": 1, "expiry": exp_far}]
                return short_leg + long_leg
            return template["legs"](atm, otm_c1, otm_c2, otm_p1, otm_p2, exp_near)
    return []


if "md_spot" in st.session_state and exps and chain_df is not None:
    with st.expander(_("mdp.suggestions"), expanded=False):
        # Aplanar catálogo para selectbox
        all_strategy_names = []
        cat_map = {}
        for cat_name, strats in _STRATEGY_CATALOG.items():
            for s_name in strats:
                all_strategy_names.append(f"{cat_name}  /  {s_name}")
                cat_map[f"{cat_name}  /  {s_name}"] = (cat_name, s_name)

        sg1, sg2, sg3, sg4 = st.columns([3, 2, 1, 1])
        with sg1:
            chosen_label = st.selectbox(_("mdp.strategy"), all_strategy_names, key="sug_strategy")
        _unused, chosen_name = cat_map[chosen_label]
        template_info = None
        for cat in _STRATEGY_CATALOG.values():
            if chosen_name in cat:
                template_info = cat[chosen_name]
                break

        # Vencimiento "cercano" (>=21 días)
        today_dt = datetime.now().date()
        near_exps = [e for e in exps if (datetime.strptime(str(e)[:10], "%Y-%m-%d").date() - today_dt).days >= 21]
        near_exps = near_exps or exps
        far_exps  = exps[min(1, len(exps)-1):]

        with sg2:
            exp_near_sel = st.selectbox(
                _("mdp.exp_near"), near_exps, index=0, key="sug_exp_near",
                format_func=fmt_expiry,
            )
            exp_near_sel = fmt_expiry(exp_near_sel)
        with sg3:
            spread_pct_sel = st.number_input(_("mdp.spread_pct"), value=5.0, min_value=1.0, max_value=30.0,
                                             step=1.0, format="%.0f", key="sug_spread",
                                             help=_("mdp.spread_help"))
        with sg4:
            st.write("")
            is_calendar = template_info.get("two_expiry", False) if template_info else False

        # Para calendars: elegir también vencimiento lejano
        exp_far_sel = exp_near_sel
        if is_calendar and len(exps) > 1:
            idx_near = exps.index(exp_near_sel) if exp_near_sel in exps else 0
            far_opts = exps[idx_near + 1:] if idx_near + 1 < len(exps) else exps
            exp_far_sel = st.selectbox(
                _("mdp.exp_far"), far_opts, index=0, key="sug_exp_far",
                format_func=fmt_expiry,
            )
            exp_far_sel = fmt_expiry(exp_far_sel)

        if template_info:
            st.info(f"**{chosen_name}** — {template_info['desc']}")
            if "note" in template_info:
                st.warning(template_info["note"])

        # Preview de los legs que se van a crear
        strikes_near = _strikes_for_expiry(exp_near_sel)
        if strikes_near and spot > 0:
            preview_legs = _build_strategy_legs(chosen_name, spot, strikes_near,
                                                exp_near_sel, exp_far_sel, spread_pct_sel)
            if preview_legs:
                prev_rows = []
                costo_preview = 0.0
                for i, lg in enumerate(preview_legs):
                    bid_p, ask_p, last_p = _bid_ask_last_from_chain(lg["strike"], lg["type"], lg["expiry"])
                    mid_p = round((bid_p + ask_p) / 2, 3) if bid_p is not None and ask_p is not None else None
                    pm_p  = mid_p if mid_p is not None else (last_p or 0.0)
                    costo_preview += lg["qty"] * LOTES * pm_p
                    prev_rows.append({
                        "Leg": i + 1,
                        "Tipo": lg["type"].upper(),
                        "Dir": "LONG" if lg["qty"] > 0 else "SHORT",
                        "Qty": abs(lg["qty"]),
                        "Strike": fmt_strike_label(lg["strike"]),
                        "Expiry": fmt_expiry(lg["expiry"]),
                        "Mid (= Pagado)": f"${pm_p:.2f}" if pm_p else "—",
                        "Costo leg": f"${lg['qty'] * LOTES * pm_p:+,.0f}",
                    })
                st.dataframe(pd.DataFrame(prev_rows).set_index("Leg"), use_container_width=True,
                             height=min(200, 75 + len(prev_rows) * 35))
                sign = "+" if costo_preview >= 0 else ""
                label = _("mdp.net_debit") if costo_preview > 0 else _("mdp.net_credit")
                st.caption(f"**{label}:** ${sign}{costo_preview:,.2f}  ·  {_('mdp.paid_mid')}")

        sa, sb = st.columns([2, 2])
        with sa:
            reemplazar = st.checkbox(_("mdp.replace_legs"), value=True, key="sug_reemplazar")
        with sb:
            if st.button(_("mdp.apply_strategy"), type="primary", key="sug_apply"):
                if not strikes_near:
                    st.error(_("mdp.no_strikes"))
                elif spot <= 0:
                    st.error(_("mdp.load_price_first"))
                else:
                    new_legs = _build_strategy_legs(chosen_name, spot, strikes_near,
                                                    exp_near_sel, exp_far_sel, spread_pct_sel)
                    if new_legs:
                        built = []
                        for lg in new_legs:
                            bid_l, ask_l, last_l = _bid_ask_last_from_chain(lg["strike"], lg["type"], lg["expiry"])
                            mid_l = round((bid_l + ask_l) / 2, 3) if bid_l is not None and ask_l is not None else None
                            pm    = mid_l if mid_l is not None else (last_l or 0.0)
                            built.append({
                                "expiry": fmt_expiry(lg["expiry"]),
                                "strike": norm_strike(lg["strike"]),
                                "type":   lg["type"],
                                "qty":    lg["qty"],
                                "precio_mercado":        pm,
                                "precio_mercado_source": "mid",
                                "precio_pagado":         pm,
                                "sigma":                 0.25,
                            })
                        if reemplazar:
                            st.session_state["md_strat_legs"] = built
                        else:
                            st.session_state["md_strat_legs"].extend(built)
                        st.session_state.pop("esc_cached", None)
                        st.session_state.pop("esc_computed_sigmas", None)
                        st.session_state.pop("esc_params", None)
                        st.session_state.pop("esc_result", None)
                        st.success(_("mdp.strategy_applied", n=len(new_legs), name=chosen_name))
                        st.rerun()
                    else:
                        st.error(_("mdp.build_error"))

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# CONSTRUIR ESTRATEGIA — Stock
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("mdp.build_strategy"))
st.markdown(_("mdp.stock"))
col_ph, col_pc, col_qty = st.columns([1.5, 1.5, 1])
with col_ph:
    st.metric(_("mdp.price_today"), f"${spot:.2f}" if "md_spot" in st.session_state else "—")
with col_pc:
    stock_comprado = st.number_input(
        _("mdp.price_bought"),
        value=round(spot, 2) if spot else 0.0, min_value=0.0, step=0.01, format="%.2f",
        help=_("mdp.price_bought_help"),
        key="strat_stock_price",
    )
with col_qty:
    stock_qty = st.number_input(
        _("mdp.stock_qty"),
        value=0, min_value=0, step=1,
        help=_("mdp.stock_qty_help"), key="strat_stock_qty",
    )


# ════════════════════════════════════════════════════════════════════════════
# LEGS — agregar / limpiar
# ════════════════════════════════════════════════════════════════════════════

if "md_strat_legs" not in st.session_state:
    st.session_state["md_strat_legs"] = []

st.markdown(_("mdp.options"))
ab, cb = st.columns([1, 1])
with ab:
    if st.button(_("mdp.add_option"), key="add_leg"):
        if chain_df is None or chain_df.empty:
            st.warning(_("mdp.load_ticker_first"))
        elif exps:
            first_exp  = fmt_expiry(exps[0])
            strikes    = _strikes_for_expiry(first_exp)
            # Find strike closest to spot
            atm_strike = norm_strike(min(strikes, key=lambda x: abs(x - spot)) if strikes else spot)
            st.session_state["md_strat_legs"].append({
                "expiry": first_exp, "strike": atm_strike, "type": "call",
                "qty": 1, "precio_mercado": 0.0, "precio_mercado_source": "last",
                "precio_pagado": 0.0, "sigma": 0.25,
            })
            st.session_state.pop("esc_cached", None)
            st.session_state.pop("esc_params", None)
            st.session_state.pop("esc_result", None)
            st.rerun()
        else:
            st.warning(_("mdp.no_expirations"))
with cb:
    if st.session_state["md_strat_legs"]:
        if st.button(_("mdp.clear_strategy"), key="clear_legs"):
            st.session_state["md_strat_legs"] = []
            st.session_state.pop("esc_cached", None)
            st.session_state.pop("esc_computed_sigmas", None)
            st.session_state.pop("esc_params", None)
            st.session_state.pop("esc_result", None)
            st.rerun()

# ── Tabla resumen compacta ────────────────────────────────────────────────────
if st.session_state["md_strat_legs"]:
    legs_snap = st.session_state["md_strat_legs"]
    strat_name = _detect_strategy(legs_snap, int(stock_qty))
    if strat_name:
        st.info(f"**{strat_name}**")

    summary_rows = []
    for i, lg in enumerate(legs_snap):
        qty   = int(lg.get("qty", 1))
        bid, ask, last = _bid_ask_last_from_chain(lg.get("strike"), lg.get("type"), lg.get("expiry", ""))
        mid   = round((bid + ask) / 2, 3) if bid is not None and ask is not None else None
        iv_pct = round(float(lg.get("sigma", 0.25)) * 100, 1) if lg.get("sigma") else "—"
        summary_rows.append({
            "#": i + 1,
            "Tipo": lg.get("type", "").upper(),
            "Dir": "LONG" if qty > 0 else "SHORT",
            "Cant": abs(qty),
            "Strike": fmt_strike_label(lg.get("strike")),
            "Expiry": fmt_expiry(lg.get("expiry", "")),
            "Mid": f"${mid:.2f}" if mid is not None else "—",
            "Pagado": f"${float(lg.get('precio_pagado', 0)):.2f}",
            "IV %": iv_pct,
        })
    st.dataframe(pd.DataFrame(summary_rows).set_index("#"), use_container_width=True, height=min(200, 75 + len(summary_rows) * 35))

# ── Leg editors ───────────────────────────────────────────────────────────────
for i, leg in enumerate(st.session_state["md_strat_legs"]):
    expiry_val    = fmt_expiry(leg.get("expiry", exps[0] if exps else ""))
    strikes_avail = _strikes_for_expiry(expiry_val)
    strike_val    = norm_strike(leg.get("strike", strikes_avail[0] if strikes_avail else spot))
    opt_type_val  = leg.get("type", "call")
    qty_val       = int(leg.get("qty", 1))
    precio_pagado_val = float(leg.get("precio_pagado", 0))
    precio_src_val    = leg.get("precio_mercado_source", "last")

    with st.expander(_("mdp.option_n", n=i+1, type=opt_type_val.upper(), k=fmt_strike_label(strike_val).lstrip("$"), exp=expiry_val), expanded=False):
        hdr = st.columns([0.27, 0.19, 0.21, 0.28, 0.10, 0.23, 0.23, 0.23, 0.23, 0.22, 0.24, 0.22, 0.14])
        for col, label in zip(hdr, ["Expiry", "Strike", "Tipo", "L/S", "Cant", "Bid", "Ask", "Last", "Mid", "Usar", "Pagado", "IV %", ""]):
            with col:
                st.caption(label)

        cols = st.columns([0.27, 0.19, 0.21, 0.28, 0.10, 0.23, 0.23, 0.23, 0.23, 0.22, 0.24, 0.22, 0.14])
        with cols[0]:
            _exp_opts = list(exps) if exps else ([expiry_val] if expiry_val else [])
            if expiry_val and expiry_val not in _exp_opts:
                _exp_opts = [expiry_val] + _exp_opts
            _exp_idx = _exp_opts.index(expiry_val) if expiry_val in _exp_opts else 0
            expiry = st.selectbox(
                "Expiry",
                options=_exp_opts,
                index=_exp_idx,
                key=f"leg{i}_expiry",
                label_visibility="collapsed",
                format_func=fmt_expiry,
            )
            expiry = fmt_expiry(expiry)
        with cols[1]:
            strikes = _strikes_for_expiry(expiry)
            opts    = strikes if strikes else [strike_val]
            sidx    = nearest_strike_index(opts, strike_val)
            strike  = st.selectbox(
                "Strike",
                options=opts,
                index=sidx,
                key=f"leg{i}_strike",
                label_visibility="collapsed",
                format_func=fmt_strike_label,
            )
            strike = norm_strike(strike)
        with cols[2]:
            opt_type = st.selectbox("Tipo", options=["call", "put"],
                                    index=0 if opt_type_val == "call" else 1,
                                    key=f"leg{i}_type", label_visibility="collapsed")
        bid, ask, last = _bid_ask_last_from_chain(strike, opt_type, expiry)
        with cols[3]:
            side     = st.radio("L/S", options=["🟢 Long", "🔴 Short"],
                                index=0 if qty_val > 0 else 1, horizontal=True,
                                key=f"leg{i}_side", label_visibility="collapsed")
            qty_sign = 1 if "Long" in side else -1
        with cols[4]:
            qty_abs = st.number_input("Cant", value=abs(qty_val), min_value=1, max_value=20,
                                     step=1, key=f"leg{i}_qty", label_visibility="collapsed")
            qty = qty_sign * qty_abs
        with cols[5]:
            st.markdown(f"{'✓ ' if precio_src_val == 'bid' else ''}${bid:.2f}" if bid is not None else "—")
        with cols[6]:
            st.markdown(f"{'✓ ' if precio_src_val == 'ask' else ''}${ask:.2f}" if ask is not None else "—")
        with cols[7]:
            st.markdown(f"{'✓ ' if precio_src_val == 'last' else ''}${last:.2f}" if last is not None else "—")
        mid_val = ((bid + ask) / 2) if (bid is not None and ask is not None) else None
        with cols[8]:
            st.markdown(f"{'✓ ' if precio_src_val == 'mid' else ''}${mid_val:.2f}" if mid_val is not None else "—")
        with cols[9]:
            _src_opts = ["last", "bid", "ask", "mid"]
            _src_idx  = _src_opts.index(precio_src_val) if precio_src_val in _src_opts else 0
            precio_src = st.selectbox("Usar", options=_src_opts, index=_src_idx,
                                      key=f"leg{i}_precio_src", label_visibility="collapsed")
        with cols[10]:
            precio_pagado = st.number_input("Pagado", value=float(precio_pagado_val),
                                            min_value=0.0, step=0.01, format="%.2f",
                                            key=f"leg{i}_paid", label_visibility="collapsed")
        with cols[11]:
            # IV stored as decimal, displayed as %
            leg_sigma_val     = leg.get("sigma")
            leg_sigma_default = leg_sigma_val if leg_sigma_val is not None else 0.25
            _key_pct          = f"leg{i}_sigma_pct"
            _calc_iv_leg_ids  = st.session_state.get("_calc_iv_leg_ids", set())
            if i in _calc_iv_leg_ids:
                st.session_state[_key_pct] = round((leg_sigma_val or leg_sigma_default) * 100, 2)
                _calc_iv_leg_ids = _calc_iv_leg_ids - {i}
                st.session_state["_calc_iv_leg_ids"] = _calc_iv_leg_ids if _calc_iv_leg_ids else None
                if not _calc_iv_leg_ids:
                    st.session_state.pop("_calc_iv_leg_ids", None)
            elif _key_pct not in st.session_state:
                st.session_state[_key_pct] = round(leg_sigma_default * 100, 2)
            sigma_pct = st.number_input("IV %", min_value=1.0, max_value=300.0, step=0.5,
                                        format="%.1f", key=_key_pct, label_visibility="collapsed")
            sigma_input = sigma_pct / 100.0
        with cols[12]:
            st.write("")
            if st.button("🗑️", key=f"del_leg{i}", help=_("mdp.remove")):
                st.session_state["md_strat_legs"].pop(i)
                st.session_state.pop("esc_cached", None)
                st.session_state.pop("esc_params", None)
                st.session_state.pop("esc_result", None)
                st.rerun()

        pm_mtm = (bid if precio_src == "bid" else
                  ask if precio_src == "ask" else
                  last if precio_src == "last" else mid_val) or 0.0
        st.session_state["md_strat_legs"][i] = {
            "expiry": expiry, "strike": strike, "type": opt_type, "qty": qty,
            "precio_mercado": pm_mtm, "precio_mercado_source": precio_src,
            "precio_pagado": precio_pagado, "sigma": sigma_input,
        }

        if pm_mtm > 0 and spot > 0:
            if st.button(_("mdp.calc_iv"), key=f"calc_iv_leg{i}"):
                try:
                    from Codigo.analytics.vol_implicita import impvolfunc_bs
                    exp_str  = str(expiry)[:10]
                    exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
                    T_leg    = max((exp_date - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days, 1) / 365.0
                    _r   = st.session_state.get("esc_r", 0.05)
                    _div = st.session_state.get("esc_div", 0.0)
                    _tp  = "C" if opt_type == "call" else "P"
                    iv   = impvolfunc_bs(_tp, spot, float(strike), T_leg, _r, pm_mtm, _div)
                    st.session_state["md_strat_legs"][i]["sigma"] = round(iv, 4)
                    st.session_state["_calc_iv_leg_ids"] = {i}
                    st.session_state.pop("esc_cached", None)
                    st.session_state.pop("esc_params", None)
                    st.session_state.pop("esc_result", None)
                    st.rerun()
                except Exception as e:
                    st.error(_("mdp.iv_unavailable", e=str(e)))

if not st.session_state["md_strat_legs"]:
    st.caption(_("mdp.add_option_hint"))
    st.stop()

# Calcular IV para todos
if st.button(_("mdp.calc_iv_all"), key="calc_iv_all"):
    try:
        from Codigo.analytics.vol_implicita import impvolfunc_bs
        _r = st.session_state.get("esc_r", 0.05); _div = st.session_state.get("esc_div", 0.0)
        _updated = []
        for i, leg in enumerate(st.session_state["md_strat_legs"]):
            pm = leg.get("precio_mercado", 0)
            if pm <= 0 or spot <= 0:
                continue
            exp_str = str(leg.get("expiry", ""))[:10]
            try:
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
            except Exception:
                continue
            T_leg = max((exp_date - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days, 1) / 365.0
            _tp = "C" if leg.get("type") == "call" else "P"
            iv  = impvolfunc_bs(_tp, spot, float(leg.get("strike", 0)), T_leg, _r, pm, _div)
            st.session_state["md_strat_legs"][i]["sigma"] = round(iv, 4)
            _updated.append(i)
        st.session_state["_calc_iv_leg_ids"] = set(_updated)
        st.session_state.pop("esc_cached", None)
        st.session_state.pop("esc_params", None)
        st.session_state.pop("esc_result", None)
        st.rerun()
    except Exception as e:
        st.error(_("mdp.iv_unavailable", e=str(e)))

# ════════════════════════════════════════════════════════════════════════════
# RESUMEN: MERCADO / PAGADO / P&L
# ════════════════════════════════════════════════════════════════════════════
legs_res = st.session_state["md_strat_legs"]
valor_stock   = float(stock_qty) * float(spot)
valor_opciones = sum(int(l.get("qty", 1)) * LOTES * float(l.get("precio_mercado", 0)) for l in legs_res)
mercado_hoy   = valor_stock + valor_opciones
pagado_stock  = float(stock_qty) * float(stock_comprado or 0)
pagado_opciones = sum(int(l.get("qty", 1)) * LOTES * float(l.get("precio_pagado", 0)) for l in legs_res)
pagado        = pagado_stock + pagado_opciones
pnl_hoy       = mercado_hoy - pagado

st.markdown(_("mdp.summary"))
r1, r2, r3 = st.columns(3)
with r1:
    st.metric(_("mdp.market_today"), f"${mercado_hoy:,.2f}")
with r2:
    st.metric(_("mdp.paid_total"), f"${pagado:,.2f}")
with r3:
    color = "#dc3545" if pnl_hoy < 0 else "#28a745"
    st.markdown(_("mdp.pnl_current"))
    st.markdown(f'<span style="color:{color}; font-size:1.4rem; font-weight:700;">${pnl_hoy:+,.2f}</span>',
                unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# PARÁMETROS r / div (necesarios para Griegas + Payoff + Escenarios)
# ════════════════════════════════════════════════════════════════════════════
_r_default   = st.session_state.get("md_r",    0.05)
_div_default = st.session_state.get("md_div",  0.0)
st.session_state.setdefault("esc_r",   _r_default)
# esc_div: no setdefault aquí — el widget con key="esc_div" gestiona su estado

# ── r ────────────────────────────────────────────────────────────────────────
def _fetch_r_subprocess():
    script = Path(__file__).resolve().parent.parent / "_fetch_r.py"
    try:
        out = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                             timeout=20, cwd=_PROJECT_ROOT)
        if out.returncode == 0 and out.stdout.strip():
            val_str, src = out.stdout.strip().split("|", 1)
            return float(val_str), src
    except Exception:
        pass
    return None

if st.session_state.get("_calc_r_pending"):
    st.session_state.pop("_calc_r_pending", None)
    result = _fetch_r_subprocess()
    if result:
        r_val, r_source = result
        st.session_state["esc_r"]             = round(float(r_val), 4)
        st.session_state["esc_r_last_fetched"] = st.session_state["esc_r"]
        st.session_state["esc_r_source"]       = r_source
    else:
        st.error(_("mdp.r_fetch_error"))

# ════════════════════════════════════════════════════════════════════════════
# GRIEGAS DEL PORTFOLIO
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("mdp.greeks_portfolio"))
r_greek  = float(st.session_state.get("esc_r",  _r_default))
div_greek = float(st.session_state.get("esc_div", _div_default))

today = datetime.now().date()
total_delta = total_gamma = total_vega = total_theta = 0.0
greek_rows = []

for leg in legs_res:
    K        = float(leg.get("strike", 0))
    qty      = int(leg.get("qty", 1))
    opt_type = "C" if leg.get("type") == "call" else "P"
    sigma_lg = float(leg.get("sigma", 0.25))
    exp_str  = str(leg.get("expiry", ""))[:10]
    try:
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
        T_lg = max((exp_date - today).days, 0) / 365.0
    except Exception:
        T_lg = 0.25
    if spot > 0 and K > 0 and sigma_lg > 0:
        g = _bs_greeks(opt_type, spot, K, T_lg, r_greek, sigma_lg, div_greek)
        lote = qty * LOTES
        total_delta += lote * g["delta"]
        total_gamma += lote * g["gamma"]
        total_vega  += lote * g["vega"]
        total_theta += lote * g["theta"]
        greek_rows.append({
            "Leg": f"#{len(greek_rows)+1} {opt_type} K={K:.0f}",
            "Qty×Lote": lote,
            "Δ leg": round(lote * g["delta"], 3),
            "Γ leg": round(lote * g["gamma"], 4),
            "ν leg": round(lote * g["vega"],  2),
            "Θ leg (día)": round(lote * g["theta"], 3),
        })

if stock_qty > 0:
    total_delta += float(stock_qty) * 1.0
    greek_rows.append({
        "Leg": f"Stock ×{int(stock_qty)}",
        "Qty×Lote": stock_qty,
        "Δ leg": float(stock_qty),
        "Γ leg": 0.0, "ν leg": 0.0, "Θ leg (día)": 0.0,
    })

g1, g2, g3, g4 = st.columns(4)
with g1: st.metric("Δ Delta",        f"{total_delta:+.3f}")
with g2: st.metric("Γ Gamma",        f"{total_gamma:+.4f}")
with g3: st.metric("ν Vega ($/1%σ)", f"{total_vega:+.2f}")
with g4: st.metric("Θ Theta (día)",  f"{total_theta:+.3f}")

with st.expander(_("mdp.breakdown_leg"), expanded=False):
    df_g = pd.DataFrame(greek_rows)
    if not df_g.empty:
        total_row = pd.DataFrame([{
            "Leg": "TOTAL", "Qty×Lote": "—",
            "Δ leg": round(total_delta, 3), "Γ leg": round(total_gamma, 4),
            "ν leg": round(total_vega, 2), "Θ leg (día)": round(total_theta, 3),
        }])
        st.dataframe(pd.concat([df_g, total_row], ignore_index=True), use_container_width=True, hide_index=True)

    st.divider()

# ════════════════════════════════════════════════════════════════════════════
# PAYOFF / P&L AL VENCIMIENTO
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("mdp.payoff_pnl"))

# Rango de S inteligente
all_strikes = [float(l.get("strike", spot)) for l in legs_res]
K_min = min(all_strikes) if all_strikes else spot * 0.8
K_max = max(all_strikes) if all_strikes else spot * 1.2
S_lo  = round(K_min * 0.80, 2)
S_hi  = round(K_max * 1.20, 2)

try:
    from Codigo.analytics.payoffs import payoff_call, payoff_put
except ImportError:
    def payoff_call(S, K): return max(float(S) - float(K), 0.0)
    def payoff_put(S, K):  return max(float(K) - float(S), 0.0)

# T_max para compounding del costo
exp_dates = []
for lg in legs_res:
    try:
        exp_dates.append(datetime.strptime(str(lg.get("expiry",""))[:10], "%Y-%m-%d").date())
    except Exception:
        pass
T_max_pay = max((d - today).days for d in exp_dates) / 365.0 if exp_dates else 0.25
costo_pagado_fv = pagado * np.exp(r_greek * T_max_pay) if pagado != 0 else 0.0

# Vectorized payoff
S_chart = np.linspace(S_lo, S_hi, 400)
payoff_opts = np.zeros_like(S_chart)
for lg in legs_res:
    K   = float(lg.get("strike", 0))
    qty = int(lg.get("qty", 1))
    if lg.get("type") == "call":
        payoff_opts += qty * LOTES * np.maximum(S_chart - K, 0)
    else:
        payoff_opts += qty * LOTES * np.maximum(K - S_chart, 0)
payoff_stock  = float(stock_qty) * (S_chart - float(stock_comprado or 0))
payoff_total  = payoff_opts + payoff_stock
pnl_total     = payoff_total - costo_pagado_fv
breakevens    = _find_breakevens(S_chart, pnl_total)
max_pnl_idx   = int(np.argmax(pnl_total))
min_pnl_idx   = int(np.argmin(pnl_total))

fig_p, ax_p = plt.subplots(figsize=(11, 4.5), dpi=100)

# Fill areas
ax_p.fill_between(S_chart, pnl_total, 0,
                  where=(pnl_total >= 0), color="#28a745", alpha=0.18, label="_nolegend_")
ax_p.fill_between(S_chart, pnl_total, 0,
                  where=(pnl_total <  0), color="#dc3545", alpha=0.18, label="_nolegend_")

# Curves
ax_p.plot(S_chart, payoff_total, "--", color="#888888", linewidth=1.4, label=_("me.payoff_no_cost"))
ax_p.plot(S_chart, pnl_total, color="#1f77b4", linewidth=2.2,
          label=f"P&L  (costo FV = ${costo_pagado_fv:,.0f})")
ax_p.axhline(0, color="black", linewidth=0.7, linestyle="-")

# Spot actual
if spot > 0:
    ax_p.axvline(spot, color="#2ca02c", linewidth=1.3, linestyle="--", alpha=0.9, label=f"Spot = {spot:.2f}")

# Strikes
for K in sorted(set(all_strikes)):
    ax_p.axvline(K, color="#ff7f0e", linewidth=0.9, linestyle=":", alpha=0.7, label=f"K={K:.0f}")

# Break-even
for be in breakevens:
    ax_p.axvline(be, color="#9467bd", linewidth=1.1, linestyle="--", alpha=0.75)
    ax_p.annotate(f"BE\n${be:.2f}", xy=(be, 0), xytext=(be, (pnl_total.max() - pnl_total.min()) * 0.07),
                  fontsize=7.5, ha="center", color="#9467bd",
                  arrowprops=dict(arrowstyle="-", color="#9467bd", lw=0.8))

# Max / min
ax_p.axhline(pnl_total[max_pnl_idx], color="#28a745", linewidth=0.9, linestyle=":", alpha=0.7)
ax_p.axhline(pnl_total[min_pnl_idx], color="#dc3545", linewidth=0.9, linestyle=":", alpha=0.7)

ax_p.set_xlabel(_("me.xlabel_underlying"), fontsize=10)
ax_p.set_ylabel(_("me.ylabel_pnl"), fontsize=10)
ax_p.set_title(_("me.title_pnl", name=loaded_ticker), fontsize=11)
handles, labels = ax_p.get_legend_handles_labels()
seen = {}
for h, l in zip(handles, labels):
    if l not in seen:
        seen[l] = h
ax_p.legend(seen.values(), seen.keys(), fontsize=8, loc="best")
ax_p.grid(True, alpha=0.2)
plt.tight_layout()
st.pyplot(fig_p, use_container_width=True)
plt.close(fig_p)

# Resumen P&L tabular
st.markdown(_("mdp.pnl_summary"))
pnl_summary_data = {
    _("me.concept"): [
        _("mdp.max_gain"), _("mdp.max_loss"),
        _("mdp.breakevens"),
        _("mdp.cost_fv"),
    ],
    _("mdp.value_usd"): [
        f"${pnl_total[max_pnl_idx]:,.2f}" if not np.isinf(pnl_total[max_pnl_idx]) else "Ilimitada",
        f"${pnl_total[min_pnl_idx]:,.2f}" if not np.isinf(abs(pnl_total[min_pnl_idx])) else "Ilimitada",
        ", ".join([f"${b}" for b in breakevens]) if breakevens else "—",
        f"${costo_pagado_fv:,.2f}",
    ],
    _("me.s_level"): [
        f"${S_chart[max_pnl_idx]:.2f}",
        f"${S_chart[min_pnl_idx]:.2f}",
        "—", "—",
    ],
}
st.dataframe(pd.DataFrame(pnl_summary_data), use_container_width=True, hide_index=True)
st.caption(_("mdp.fv_caption", paid=f"{pagado:,.2f}", r=f"{r_greek:.4f}", t=f"{T_max_pay:.3f}", fv=f"{costo_pagado_fv:,.2f}"))

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# ESCENARIOS
# ════════════════════════════════════════════════════════════════════════════
with st.expander(_("mdp.scenarios_howto"), expanded=False):
    st.markdown(_("mdp.scenarios_help"))
st.subheader(_("mdp.scenarios"))

try:
    from Codigo.data.market_data import get_dividend_yield as _get_div
except ImportError:
    _get_div = lambda t: 0.0

try:
    from Codigo.analytics.payoffs import payoff_call as _pcall, payoff_put as _pput
except ImportError:
    _pcall = payoff_call; _pput = payoff_put

try:
    from Codigo.pricing import (
        opcion_americana_bs, opcion_americana_bs_ql,
        opcion_americana_bin, opcion_americana_bin_ql,
        opcion_americana_mc, opcion_americana_mc_ql,
        opcion_americana_fd, opcion_americana_fd_ql,
        _QL_AVAILABLE,
    )
except ImportError:
    from Codigo.pricing import opcion_americana_bs, opcion_americana_bin, opcion_americana_mc, opcion_americana_fd
    opcion_americana_bs_ql = opcion_americana_bin_ql = opcion_americana_mc_ql = opcion_americana_fd_ql = None
    _QL_AVAILABLE = False


def _price_opt(tipo, S, K, T, r, sigma, div, model, pasos, M):
    if T <= 0:
        return float(_pcall(S, K) if tipo == "C" else _pput(S, K))
    if model == "BAW":
        fn = opcion_americana_bs_ql if (_QL_AVAILABLE and opcion_americana_bs_ql) else opcion_americana_bs
        return fn(tipo, S, K, T, r, sigma, div)
    if model == "Binomial":
        fn = opcion_americana_bin_ql if (_QL_AVAILABLE and opcion_americana_bin_ql) else opcion_americana_bin
        return fn(tipo, S, K, T, r, sigma, div, pasos)
    if model == "Monte Carlo":
        fn = opcion_americana_mc_ql if (_QL_AVAILABLE and opcion_americana_mc_ql) else opcion_americana_mc
        return fn(tipo, S, K, T, r, sigma, div, pasos)
    if model == "Diferencias finitas":
        fn = opcion_americana_fd_ql if (_QL_AVAILABLE and opcion_americana_fd_ql) else opcion_americana_fd
        return fn(tipo, S, K, T, r, sigma, div, M)
    return opcion_americana_bs(tipo, S, K, T, r, sigma, div)


def _days_to_expiry(expiry_str):
    try:
        exp = datetime.strptime(str(expiry_str)[:10], "%Y-%m-%d")
        return max(0, (exp - datetime.now()).days)
    except Exception:
        return 365

# Sigma default from farthest leg
_sigma_default = st.session_state.get("md_sigma", 0.25)
try:
    if chain_df is not None and not chain_df.empty:
        from Codigo.data.market_data import get_implied_vol_atm as _giv_atm
        _exp_max = max(legs_res, key=lambda l: _days_to_expiry(l.get("expiry", "")), default={}).get("expiry", "")
        if _exp_max:
            _sa = _giv_atm(chain_df, spot, _exp_max)
            if _sa:
                _sigma_default = round(_sa, 4)
except Exception:
    pass

# ── Grilla ───────────────────────────────────────────────────────────────────
st.markdown(_("mdp.grid"))
g1, g2, g3, g4 = st.columns(4)
with g1:
    n_cols = st.number_input(_("mdp.cols_time"), value=4, min_value=2, max_value=20, step=1, key="esc_ncol")
with g2:
    n_rows = st.number_input(_("mdp.rows_price"), value=11, min_value=3, max_value=51, step=2, key="esc_nrow")
with g3:
    S_desde = st.number_input(_("mdp.s_from"), value=round(S_lo, 1), min_value=0.1, step=1.0, format="%.1f", key="esc_s_desde")
with g4:
    S_a = st.number_input(_("mdp.s_to"), value=round(S_hi, 1), min_value=0.1, step=1.0, format="%.1f", key="esc_s_a")

# ── Parámetros ────────────────────────────────────────────────────────────────
st.markdown(_("mdp.params"))
p1, p2 = st.columns(2)
with p1:
    st.markdown("r (^IRX)")
    r_row = st.columns([1, 0.35])
    with r_row[0]:
        r = st.number_input("r", value=float(st.session_state["esc_r"]),
                            format="%.4f", step=0.001, key="esc_r_val", label_visibility="collapsed")
        st.session_state["esc_r"] = r
    with r_row[1]:
        if st.button(_("mdp.calculate"), key="calc_r"):
            st.session_state["_calc_r_pending"] = True
            st.rerun()
    if st.session_state.get("esc_r_last_fetched") is not None:
        st.caption(f"✓ {st.session_state.get('esc_r_source','?')} → {r*100:.2f}%")
with p2:
    st.markdown("div (dividendYield)")
    d_row = st.columns([1, 0.35])
    with d_row[0]:
        div = st.number_input("div", value=float(st.session_state.get("esc_div", _div_default)),
                              format="%.4f", step=0.001, key="esc_div", label_visibility="collapsed")
    with d_row[1]:
        def _calc_div():
            _tk = st.session_state.get("md_ticker", loaded_ticker or "")
            if _tk:
                dv = _get_div(_tk)
                st.session_state["esc_div"] = round(dv, 4)
                st.session_state["esc_div_last_fetched"] = dv
                st.session_state["esc_div_source"] = "dividendYield" if dv > 0 else "dividendYield (0)"
        if st.button(_("mdp.calculate"), key="calc_div", on_click=_calc_div):
            if not loaded_ticker:
                st.warning(_("mdp.load_ticker_first"))
    if st.session_state.get("esc_div_last_fetched") is not None:
        st.caption(f"✓ {st.session_state.get('esc_div_source','?')} → {div*100:.2f}%")

# ── Modelo ────────────────────────────────────────────────────────────────────
st.markdown(_("mdp.model"))
col_mod, col_pasos, col_M = st.columns(3)
with col_mod:
    modelo = st.selectbox(_("mdp.model_select"),
            options=["BAW", "Binomial", "Monte Carlo", "Diferencias finitas"],
        index=0, key="esc_modelo",
        help=_("mdp.model_help"))
with col_pasos:
    pasos = st.number_input(_("mdp.steps"), value=100, min_value=10,
            max_value=500 if modelo == "Binomial" else 50000,
            step=50 if modelo == "Binomial" else 1000,
        key="esc_pasos", disabled=(modelo in ("BAW", "Diferencias finitas")))
with col_M:
    M_fd = st.number_input("M (FD)", value=150, min_value=20, max_value=500,
        step=10, key="esc_M", disabled=(modelo != "Diferencias finitas"))

st.caption(f"r={r:.4f}  |  div={div:.4f}  |  Modelo: **{modelo}**  |  IV por leg")

# ── Invalidar caché si cambiaron parámetros o sigmas ──────────────────────────
_current_sigmas  = tuple(lg.get("sigma") for lg in legs_res)
_computed_sigmas = st.session_state.get("esc_computed_sigmas")
_esc_params = (
    n_rows, n_cols, S_desde, S_a, modelo, pasos, M_fd, r, div,
    stock_qty, stock_comprado,
    tuple((lg.get("strike"), lg.get("qty"), str(lg.get("expiry", "")), lg.get("sigma")) for lg in legs_res),
)
_stored_params = st.session_state.get("esc_params")
if _computed_sigmas is not None and _current_sigmas != _computed_sigmas:
    st.session_state.pop("esc_cached", None)
    st.session_state.pop("esc_computed_sigmas", None)
    st.session_state.pop("esc_params", None)
    st.session_state.pop("esc_result", None)
elif _stored_params is not None and _esc_params != _stored_params:
    st.session_state.pop("esc_cached", None)
    st.session_state.pop("esc_computed_sigmas", None)
    st.session_state.pop("esc_params", None)
    st.session_state.pop("esc_result", None)

calc_esc = st.button(
    _("mdp.recalc_scenarios") if st.session_state.get("esc_cached") else _("mdp.calc_scenarios"),
    type="primary", key="calc_escenarios",
)
if calc_esc:
    st.session_state["esc_cached"] = True
    st.session_state.pop("esc_result", None)  # forzar recálculo

if not st.session_state.get("esc_cached"):
    st.info(_("mdp.click_calc"))
    st.stop()

# ── Usar resultado cacheado si existe y params coinciden ──────────────────────
mat = df_esc = df_pnl = date_cols = unique_cols = row_labels = costo_pagado_mtx = n_cols_actual = None
if _stored_params is not None and _esc_params == _stored_params:
    _cached = st.session_state.get("esc_result")
    if _cached is not None:
        mat, df_esc, df_pnl, date_cols, unique_cols, row_labels, costo_pagado_mtx, n_cols_actual = _cached
        st.session_state["esc_computed_sigmas"] = _current_sigmas

if mat is None:
    # ── Build matrix ──────────────────────────────────────────────────────────
    def _parse_exp_date(e):
        try:
            return pd.to_datetime(str(e).strip()[:10]).date()
        except Exception:
            return None

    exp_dates_sc = [_parse_exp_date(lg.get("expiry", "")) for lg in legs_res]
    exp_dates_sc = [d for d in exp_dates_sc if d is not None]
    expiry_date  = max(exp_dates_sc) if exp_dates_sc else today + timedelta(days=365)
    T_max_days   = max((expiry_date - today).days, 0)
    T_max        = T_max_days / 365.0

    S_vals   = np.linspace(min(S_desde, S_a), max(S_desde, S_a), int(n_rows))
    t_vals   = [T_max * (n_cols - 1 - i) / max(1, n_cols - 1) for i in range(n_cols)]
    if n_cols >= 2 and T_max / max(1, n_cols - 1) > 1e-6:
        t_vals = t_vals[:-1] + [T_max / max(1, n_cols - 1) * 0.5, 0.0]
    n_cols_actual = len(t_vals)

    if n_cols_actual == 1:
        date_cols = [expiry_date.strftime("%d/%m/%y")]
    else:
        date_cols = []
        for j in range(n_cols_actual):
            if j == 0:
                d = today
            elif j == n_cols_actual - 1:
                d = expiry_date
            else:
                frac = j / (n_cols_actual - 1)
                d = today + timedelta(days=int(T_max_days * frac))
            date_cols.append(d.strftime("%d/%m/%y"))

    def _leg_days(e):
        try:
            d = _parse_exp_date(e)
            return (d - today).days if d else 0
        except Exception:
            return 0

    st.session_state["esc_computed_sigmas"] = _current_sigmas
    st.session_state["esc_params"] = _esc_params

    prog = st.progress(0, text=_("mdp.calculating"))
    st.caption(_("mdp.cancel_hint"))
    mat = np.zeros((int(n_rows), n_cols_actual))
    total_cells = int(n_rows) * n_cols_actual
    cell_idx = 0
    for i, S in enumerate(S_vals):
        for j, T in enumerate(t_vals):
            sv = float(stock_qty) * S
            ov = 0.0
            for lg in legs_res:
                K        = float(lg.get("strike", 0))
                qty_l    = int(lg.get("qty", 1))
                tp       = "C" if lg.get("type") == "call" else "P"
                T_ld     = max(_leg_days(lg.get("expiry", "")), 0) / 365.0
                T_eff    = T_ld - T_max + T
                sig_l    = float(lg.get("sigma", 0.25)) or 0.25
                _pasos_l = int(pasos) if modelo in ("Binomial", "Monte Carlo") else 100
                _M_l     = int(M_fd)  if modelo == "Diferencias finitas" else 150
                if T_eff <= 0:
                    p = float(_pcall(S, K) if tp == "C" else _pput(S, K))
                else:
                    p = _price_opt(tp, S, K, T_eff, r, sig_l, div, modelo, _pasos_l, _M_l)
                ov += qty_l * LOTES * p
            mat[i, j] = sv + ov
            cell_idx += 1
            if total_cells > 0 and cell_idx % max(1, total_cells // 20) == 0:
                prog.progress(min(1.0, cell_idx / total_cells), text=f"Calculando... {cell_idx}/{total_cells}")
    prog.progress(1.0, text="Listo")
    prog.empty()

    # Garantizar columnas e índice únicos (pandas Styler falla con duplicados)
    def _unique_labels(labels: list) -> list:
        seen: dict = {}
        result = []
        for lb in labels:
            if lb in seen:
                seen[lb] += 1
                result.append(f"{lb}_{seen[lb]}")
            else:
                seen[lb] = 0
                result.append(lb)
        return result

    unique_cols = _unique_labels(date_cols)
    row_labels  = _unique_labels([f"S={s:.1f}" for s in S_vals])

    df_esc = pd.DataFrame(mat, index=row_labels, columns=unique_cols)
    df_esc = df_esc.iloc[::-1].round(1)

    costo_pagado_mtx = (float(stock_qty) * float(stock_comprado or 0) +
                        sum(int(lg.get("qty", 1)) * LOTES * float(lg.get("precio_pagado", 0)) for lg in legs_res))
    df_pnl = (df_esc - costo_pagado_mtx).round(1)

    st.session_state["esc_result"] = (mat, df_esc, df_pnl, date_cols, unique_cols, row_labels, costo_pagado_mtx, n_cols_actual)


def _gradient_style(df, ref, fmt="{:.1f}"):
    v_min, v_max = df.values.min(), df.values.max()
    rng_neg = ref - v_min if v_min < ref else 1
    rng_pos = v_max - ref if v_max > ref else 1

    def _s(v):
        if pd.isna(v):
            return ""
        if v < ref:
            a = min(1, max(0, 0.2 + 0.6 * (ref - v) / rng_neg)) if rng_neg > 0 else 0.8
            return f"background-color: rgba(220,53,69,{a:.2f}); color: {'#fff' if a>0.55 else '#1a1a1a'}; font-weight:500"
        elif v > ref:
            a = min(1, max(0, 0.2 + 0.6 * (v - ref) / rng_pos)) if rng_pos > 0 else 0.8
            return f"background-color: rgba(40,167,69,{a:.2f}); color: {'#fff' if a>0.55 else '#1a1a1a'}; font-weight:500"
        return "background-color:rgba(128,128,128,0.15); color:#1a1a1a"

    return df.style.format(fmt).applymap(_s)


def _esc_column_config(cols, pct=False):
    fmt = "%.1f%%" if pct else "%.1f"
    return {c: st.column_config.NumberColumn(c, format=fmt) for c in cols}


# T_max y costo FV para %PnL
_exp_dates_mdp = []
for _lg in legs_res:
    try:
        d = pd.to_datetime(str(_lg.get("expiry", "")).strip()[:10]).date()
        _exp_dates_mdp.append(d)
    except Exception:
        pass
_expiry_mdp = max(_exp_dates_mdp) if _exp_dates_mdp else today + timedelta(days=365)
_T_max_days_mdp = max((_expiry_mdp - today).days, 0)
_T_max_mdp = _T_max_days_mdp / 365.0
_r_esc_mdp = float(st.session_state.get("esc_r", 0.05))
costo_fv_mdp = costo_pagado_mtx * np.exp(_r_esc_mdp * _T_max_mdp) if costo_pagado_mtx != 0 else 1.0
df_pct_pnl = (df_pnl / costo_fv_mdp * 100).round(1) if costo_fv_mdp != 0 else df_pnl * 0

def _vista_label(key, default):
    t = _(key)
    return default if t == key else t

tabla_vista = st.radio(
    _vista_label("mdp.vista", "Vista"),
    options=["PnL", "Valor", "%PnL"],
    format_func=lambda x: _vista_label(
        {"PnL": "mdp.view_pnl", "Valor": "mdp.view_valor", "%PnL": "mdp.view_pct_pnl"}[x],
        {"PnL": "P&L (valor − pagado)", "Valor": "Valor de la estrategia", "%PnL": "%PnL (P&L / FV pagado)"}[x],
    ),
    horizontal=True,
    index=0,
    key="mdp_esc_tabla_vista",
)
if tabla_vista == "Valor":
    df_show = df_esc
    ref_show = costo_pagado_mtx
    fmt_show = "{:.1f}"
    pct_show = False
elif tabla_vista == "%PnL":
    df_show = df_pct_pnl
    ref_show = 0
    fmt_show = "{:.1f}%"
    pct_show = True
else:
    df_show = df_pnl
    ref_show = 0
    fmt_show = "{:.1f}"
    pct_show = False

st.dataframe(
    _gradient_style(df_show, ref_show, fmt=fmt_show),
    use_container_width=False,
    height=max(400, min(600, 32 * len(df_show) + 50)),
    column_config=_esc_column_config(unique_cols, pct=pct_show),
)

# ── Gráfico de líneas de escenarios ──────────────────────────────────────────
st.markdown(_("mdp.curves_pnl"))
colors_sc = plt.cm.tab10(np.linspace(0, 1, n_cols_actual))
fig_sc, ax_sc = plt.subplots(figsize=(11, 4), dpi=100)
# Parse S values robustly (index may have _N suffix if duplicated)
S_labels = []
for lbl in df_pnl.index:
    try:
        S_labels.append(float(lbl.split("=")[1].split("_")[0]))
    except Exception:
        S_labels.append(0.0)
for j_col, col_name in enumerate(unique_cols):
    vals = df_pnl[col_name].values
    # Display label: use original date_cols (before dedup suffix)
    disp_label = date_cols[j_col] if j_col < len(date_cols) else col_name
    lw   = 2.4 if j_col == 0 else (2.0 if j_col == len(unique_cols) - 1 else 1.3)
    ls   = "-" if j_col in (0, len(unique_cols) - 1) else "--"
    ax_sc.plot(S_labels, vals, color=colors_sc[j_col], linewidth=lw, linestyle=ls, label=disp_label)
ax_sc.axhline(0, color="black", linewidth=0.8)
if S_lo <= spot <= S_hi:
    ax_sc.axvline(spot, color="#2ca02c", linewidth=1.2, linestyle="--", alpha=0.85, label=f"Spot={spot:.2f}")
for K in sorted(set(all_strikes)):
    ax_sc.axvline(K, color="#ff7f0e", linewidth=0.8, linestyle=":", alpha=0.6, label=f"K={K:.0f}")
ax_sc.set_xlabel(_("me.xlabel_underlying"), fontsize=10)
ax_sc.set_ylabel(_("me.ylabel_pnl"), fontsize=10)
ax_sc.set_title(_("mdp.pnl_moments", ticker=loaded_ticker), fontsize=11)
handles, labels = ax_sc.get_legend_handles_labels()
seen_sc = {}
for h, lb in zip(handles, labels):
    if lb not in seen_sc:
        seen_sc[lb] = h
ax_sc.legend(seen_sc.values(), seen_sc.keys(), fontsize=8, loc="best")
ax_sc.grid(True, alpha=0.2)
plt.tight_layout()
st.pyplot(fig_sc, use_container_width=True)
plt.close(fig_sc)

# ── Exportar ──────────────────────────────────────────────────────────────────
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as xl:
    df_esc.to_excel(xl, sheet_name="Valor estrategia")
    df_pnl.to_excel(xl, sheet_name="P&L")
    df_pct_pnl.to_excel(xl, sheet_name="%PnL")
buf.seek(0)
_tk = st.session_state.get("md_ticker", ticker or "estrategia")
fn  = f"escenarios_{_tk}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
st.download_button(_("mdp.export_scenarios"), data=buf.getvalue(), file_name=fn,
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   key="mdp_export_esc")
