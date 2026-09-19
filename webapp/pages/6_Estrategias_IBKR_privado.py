# -*- coding: utf-8 -*-
"""
Estrategias IBKR (privado) — Sube una captura de IBKR y extrae la estrategia para valuarla.
Usa OCR local (EasyOCR) para interpretar screenshots de la app IBKR.
"""
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
_IBKR_POSITIONS_FILE = _WEBAPP_DIR / "ibkr_positions.json"

import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import norm

from i18n import render_language_selector

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
    div[class*="block-container"], div[class*="BlockContainer"] { max-width: none !important; }
</style>
""", unsafe_allow_html=True)

render_language_selector()

# ════════════════════════════════════════════════════════════════════════════
# HELPERS GLOBALES
# ════════════════════════════════════════════════════════════════════════════
LOTES = 100

def _bs_greeks(tipo: str, S: float, K: float, T: float, r: float,
               sigma: float, div: float = 0.0) -> dict:
    if T <= 1e-6 or sigma <= 0 or S <= 0 or K <= 0:
        d = 1.0 if (tipo == "C" and S >= K) or (tipo == "P" and S <= K) else 0.0
        return {"delta": d * (1 if tipo == "C" else -1), "gamma": 0.0, "vega": 0.0, "theta": 0.0}
    d1 = (np.log(S / K) + (r - div + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    ef = np.exp(-div * T); er = np.exp(-r * T)
    if tipo == "C":
        delta = ef * norm.cdf(d1)
        theta = (-S * ef * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 - r * K * er * norm.cdf(d2) + div * S * ef * norm.cdf(d1)) / 365
    else:
        delta = -ef * norm.cdf(-d1)
        theta = (-S * ef * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                 + r * K * er * norm.cdf(-d2) - div * S * ef * norm.cdf(-d1)) / 365
    gamma = ef * norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega  = S * ef * norm.pdf(d1) * np.sqrt(T) / 100
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta}


def _find_breakevens(S_vals: np.ndarray, pnl: np.ndarray) -> list:
    bes = []
    for i in range(len(pnl) - 1):
        if pnl[i] * pnl[i + 1] < 0:
            x = S_vals[i] - pnl[i] * (S_vals[i + 1] - S_vals[i]) / (pnl[i + 1] - pnl[i])
            bes.append(round(float(x), 2))
    return bes


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


def _empty_leg():
    return {
        "action": "comprar", "type": "call", "expiry": "",
        "strike": 100, "quantity": 1,
        "ultimo": None, "ultimo_last": None, "ultimo_mid": None,
        "ultimo_bid": None, "ultimo_ask": None,
        "sigma": 0.25, "precio_compra": 0.0,
    }


def _strikes_for_expiry(chain_df, expiry: str) -> list:
    """Strikes disponibles para un expiry en la chain."""
    if chain_df is None or chain_df.empty or not expiry:
        return []
    exp_col = "expiration" if "expiration" in chain_df.columns else "expirationDate"
    if exp_col not in chain_df.columns:
        return []
    sub = chain_df[chain_df[exp_col].astype(str).str[:10] == str(expiry)[:10]]
    return sorted(sub["strike"].unique().tolist()) if "strike" in sub.columns else []


def _closest_strike(strikes: list, target: float):
    if not strikes:
        return target
    return min(strikes, key=lambda x: abs(float(x) - target))


def _bid_ask_last_from_chain(chain_df, strike: float, opt_type: str, expiry: str):
    """Busca bid, ask, last en la chain. Retorna (bid, ask, last) o (None, None, None) si no encuentra."""
    if chain_df is None or chain_df.empty:
        return None, None, None
    exp_col = "expiration" if "expiration" in chain_df.columns else "expirationDate"
    strike_val = float(strike)
    exp_str = str(expiry or "")[:10]
    match = chain_df[
        (chain_df["strike"].astype(float) == strike_val) &
        (chain_df["type"].astype(str).str.lower() == str(opt_type or "call").lower()) &
        (chain_df[exp_col].astype(str).str[:10] == exp_str)
    ]
    if match.empty:
        return None, None, None
    row = match.iloc[0]
    bid = None
    if "bid" in row.index and pd.notna(row.get("bid")) and float(row.get("bid", -1)) >= 0:
        bid = float(row["bid"])
    ask = None
    if "ask" in row.index and pd.notna(row.get("ask")) and float(row.get("ask", -1)) >= 0:
        ask = float(row["ask"])
    last = row.get("lastPrice") or row.get("last") or row.get("Last")
    if last is not None and pd.notna(last) and float(last) >= 0:
        last = float(last)
    else:
        last = None
    return bid, ask, last


# ════════════════════════════════════════════════════════════════════════════
# PERSISTENCIA JSON
# ════════════════════════════════════════════════════════════════════════════
def _load_ibkr_positions() -> list:
    if not _IBKR_POSITIONS_FILE.exists():
        return []
    try:
        with open(_IBKR_POSITIONS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("positions", [])
    except Exception:
        return []


def _save_ibkr_position(name: str, ticker: str, legs: list) -> None:
    positions = _load_ibkr_positions()
    pos = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "name": name.strip() or f"{ticker} {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "ticker": ticker,
        "created": datetime.now().isoformat(),
        "legs": [
            {
                "strike":        float(l.get("strike", 0)),
                "expiry":        str(l.get("expiry", ""))[:10],
                "type":          l.get("type", "call"),
                "position":      "Long" if int(l.get("qty", 1)) > 0 else "Short",
                "quantity":      abs(int(l.get("qty", 1))),
                "precio_compra": float(l.get("precio_pagado", 0)),
                "sigma":         float(l.get("sigma", 0.25)),
            }
            for l in legs
        ],
    }
    positions.append(pos)
    with open(_IBKR_POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({"positions": positions}, f, indent=2, ensure_ascii=False)


def _delete_ibkr_position(pos_id: str) -> None:
    positions = [p for p in _load_ibkr_positions() if p.get("id") != pos_id]
    with open(_IBKR_POSITIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({"positions": positions}, f, indent=2, ensure_ascii=False)


def _saved_to_parsed(pos: dict) -> dict:
    legs = []
    for l in pos.get("legs", []):
        qty = l.get("quantity", 1) if l.get("position") == "Long" else -l.get("quantity", 1)
        legs.append({
            "action": "comprar" if qty > 0 else "vender",
            "type": l.get("type", "call"),
            "expiry": l.get("expiry", ""),
            "strike": int(l.get("strike", 0)),
            "quantity": qty,
            "price_paid": l.get("precio_compra", 0),
            "ultimo": l.get("precio_compra", 0),
            "ultimo_last": None,
            "ultimo_mid": None,
            "sigma": float(l.get("sigma", 0.25)),
            "precio_compra": float(l.get("precio_compra", 0)),
        })
    return {"ticker": pos.get("ticker", "UNKNOWN"), "legs": legs, "posicion_info": {}}


# ════════════════════════════════════════════════════════════════════════════
# PÁGINA
# ════════════════════════════════════════════════════════════════════════════
st.title("Estrategias IBKR (privado)")

with st.expander("📖 Cómo usar", expanded=False):
    st.markdown("""
1. **Paso 1**: Vanilla (1 opción) o Estrategia (2-4 opciones).
2. **Paso 2**: Manual (sin captura) o Por foto (subir captura).
3. **Manual**: Ticker → **Cargar datos** → Vencimiento (dropdown) → Strikes (dropdown) → Elegí estrategia → Cargar.
4. **Por foto**: Subí una captura → OCR automático → form pre-cargado (o NA si no pudo leer).
5. **Cargar guardada**: Posiciones previamente guardadas en JSON.
6. **Editá** cada leg: tipo, strike, expiry, cantidad, L/S, precio pagado, IV %.
7. **Traer bid/ask/last de mercado**: obtiene precios de mercado para cada opción (o NA si no se encuentra).
8. **Calcular IV** (por leg o todas) para calcular IV implícita desde precio de mercado.
9. **Cargar datos de mercado** trae spot, chain, r, div.
10. **Griegas**, **Payoff/P&L** y **Escenarios** se calculan automáticamente.
    """)

# ── Abrir estrategias guardadas ───────────────────────────────────────────────
saved_positions = _load_ibkr_positions()
with st.expander("📂 Abrir estrategias guardadas", expanded=bool(saved_positions)):
    if saved_positions:
        pos_names = [f"{p.get('name','Sin nombre')} ({p.get('ticker','?')})" for p in saved_positions]
        sel_idx = st.selectbox("Posición", range(len(pos_names)),
                               format_func=lambda i: pos_names[i], key="ibkr_load_sel")
        lc1, lc2 = st.columns([1, 1])
        with lc1:
            if st.button("Cargar posición", key="ibkr_load_btn"):
                pos = saved_positions[sel_idx]
                st.session_state["ibkr_parsed"]   = _saved_to_parsed(pos)
                st.session_state["ibkr_ticker"]   = pos.get("ticker", "").upper()
                st.session_state.pop("ibkr_from_image", None)
                st.session_state.pop("ibkr_img_bytes", None)
                st.session_state.pop("ibkr_ocr_raw", None)
                for k in list(st.session_state.keys()):
                    if k.startswith("ibkr_leg_"):
                        st.session_state.pop(k, None)
                st.rerun()
        with lc2:
            if st.button("🗑️ Eliminar esta posición", key="ibkr_delete_btn"):
                _delete_ibkr_position(saved_positions[sel_idx].get("id", ""))
                st.success("Posición eliminada.")
                st.rerun()
    else:
        st.info("No hay estrategias guardadas. Guardá una posición después de cargar y valuar.")

# ── Paso 1: Vanilla / Estrategia (Vanilla por defecto) ──────────────────────────
ibkr_mode = st.radio(
    "Paso 1: Tipo",
    options=["vanilla", "estrategia"],
    format_func=lambda x: "Vanilla (1 opción)" if x == "vanilla" else "Estrategia (2-4 opciones)",
    horizontal=True, key="ibkr_mode",
)

# ── Paso 2: Manual / Por foto ──────────────────────────────────────────────────
ibkr_input_mode = st.radio(
    "Paso 2: Entrada",
    options=["manual", "foto"],
    format_func=lambda x: "Manual (sin captura)" if x == "manual" else "Por foto (subir captura)",
    horizontal=True, key="ibkr_input_mode",
)

# Si cambia el modo de entrada, limpiar ibkr_parsed para evitar datos inconsistentes
if "ibkr_input_mode_prev" in st.session_state and st.session_state.get("ibkr_input_mode_prev") != ibkr_input_mode:
    st.session_state.pop("ibkr_parsed", None)
    st.session_state.pop("ibkr_ticker", None)
    st.session_state.pop("ibkr_img_bytes", None)
    st.session_state.pop("ibkr_ocr_raw", None)
    st.session_state.pop("ibkr_from_image", None)
    for k in list(st.session_state.keys()):
        if k.startswith("ibkr_leg_"):
            st.session_state.pop(k, None)
st.session_state["ibkr_input_mode_prev"] = ibkr_input_mode

# ── Rama Manual: Ticker → Fetch → Expiry dropdown → Ks dropdown ─────────────────
if ibkr_input_mode == "manual":
    from Codigo.pricing import ESTRATEGIA_PIERNAS

    _ESTR_NOMBRES = {
        "straddle": "Straddle", "short_straddle": "Short Straddle",
        "strangle": "Strangle", "short_strangle": "Short Strangle",
        "bull_call_spread": "Bull Call Spread", "bear_call_spread": "Bear Call Spread",
        "bull_put_spread": "Bull Put Spread",  "bear_put_spread": "Bear Put Spread",
        "call_butterfly": "Call Butterfly", "put_butterfly": "Put Butterfly",
        "iron_condor": "Iron Condor", "iron_butterfly": "Iron Butterfly",
        "condor": "Condor", "combo": "Combo (Risk Reversal)", "collar": "Collar",
        "box": "Box", "covered_call": "Covered Call",
        "protective_put": "Protective Put", "ratio_spread": "Ratio Spread",
    }

    st.markdown("**Entrada manual**")
    t1, t2 = st.columns([3, 1])
    with t1:
        if "ibkr_manual_ticker" not in st.session_state:
            st.session_state["ibkr_manual_ticker"] = "AAPL"
        ticker_manual = st.text_input("Ticker", key="ibkr_manual_ticker").strip().upper() or ""
    with t2:
        st.write("")
        fetch_btn = st.button("Cargar datos", type="primary", key="ibkr_manual_fetch")

    if fetch_btn and ticker_manual:
        _orig_stderr = sys.stderr
        try:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")
        except Exception:
            pass
        try:
            with st.spinner(f"Cargando {ticker_manual}..."):
                from Codigo.data.market_data import get_spot, get_expirations, get_options_chain
                try:
                    from Codigo.data.market_data import get_dividend_yield, get_risk_free_rate
                except ImportError:
                    get_dividend_yield = lambda t: 0.0
                    get_risk_free_rate = lambda: 0.05
                spot_new = get_spot(ticker_manual)
                exps_new = get_expirations(ticker_manual)
                chain_new = get_options_chain(ticker_manual, None)
                st.session_state["ibkr_manual_spot"] = spot_new
                st.session_state["ibkr_manual_exps"] = exps_new or []
                st.session_state["ibkr_manual_chain"] = chain_new
                st.session_state["ibkr_div"] = round(get_dividend_yield(ticker_manual), 4)
                st.session_state["ibkr_r"] = round(get_risk_free_rate(), 4)
                st.rerun()
        except Exception as e:
            st.error(f"No se pudo cargar: {e}")
        finally:
            try:
                if sys.stderr != _orig_stderr:
                    sys.stderr.close()
                sys.stderr = _orig_stderr
            except Exception:
                pass

    exps_manual = st.session_state.get("ibkr_manual_exps", [])
    chain_manual = st.session_state.get("ibkr_manual_chain")
    spot_manual = st.session_state.get("ibkr_manual_spot", 0.0)

    if not exps_manual or chain_manual is None or chain_manual.empty:
        st.info("Ingresá un ticker y hacé clic en **Cargar datos** para obtener vencimientos y strikes.")
        if not st.session_state.get("ibkr_parsed"):
            st.stop()
    else:
        expiry_manual = st.selectbox("Vencimiento", options=exps_manual, key="ibkr_manual_expiry",
                                    format_func=lambda x: str(x)[:10] if x else "")
        strikes_manual = _strikes_for_expiry(chain_manual, str(expiry_manual)[:10])
        exp_str = str(expiry_manual)[:10]

        if not strikes_manual:
            st.warning("No hay strikes para ese vencimiento.")
        else:
            K_ref = _closest_strike(strikes_manual, spot_manual) if spot_manual else strikes_manual[len(strikes_manual)//2]

            if ibkr_mode == "vanilla":
                st.markdown("**Opción única (Vanilla)**")
                v1, v2, v3 = st.columns(3)
                with v1:
                    strike_manual = st.selectbox("Strike", options=strikes_manual,
                                                 index=strikes_manual.index(K_ref) if K_ref in strikes_manual else 0,
                                                 key="ibkr_manual_strike")
                with v2:
                    opt_type_manual = st.selectbox("Tipo", ["call", "put"], key="ibkr_manual_type")
                with v3:
                    side_manual = st.selectbox("L/S", ["Long", "Short"], key="ibkr_manual_side")
                if st.button("Cargar opción", key="ibkr_manual_load_vanilla"):
                    qty = 1 if side_manual == "Long" else -1
                    action = "comprar" if qty > 0 else "vender"
                    strike_val = int(strike_manual) if isinstance(strike_manual, (int, float)) else int(float(strike_manual))
                    leg = {
                        "action": action, "type": opt_type_manual,
                        "expiry": exp_str, "strike": strike_val, "quantity": qty,
                        "ultimo": None, "ultimo_last": None, "ultimo_mid": None,
                        "ultimo_bid": None, "ultimo_ask": None,
                        "sigma": 0.25, "precio_compra": 0.0,
                    }
                    bid, ask, last = _bid_ask_last_from_chain(chain_manual, strike_val, opt_type_manual, exp_str)
                    if bid is not None: leg["ultimo_bid"] = round(float(bid), 3)
                    if ask is not None: leg["ultimo_ask"] = round(float(ask), 3)
                    if last is not None: leg["ultimo_last"] = round(float(last), 3)
                    if bid is not None and ask is not None: leg["ultimo_mid"] = round((bid + ask) / 2, 3)
                    leg["ultimo"] = leg.get("ultimo_last") or leg.get("ultimo_mid") or leg.get("ultimo_bid") or leg.get("ultimo_ask")
                    st.session_state["ibkr_parsed"] = {"ticker": ticker_manual, "legs": [leg], "posicion_info": {}}
                    st.session_state["ibkr_ticker"] = ticker_manual
                    st.session_state["_ibkr_spot_update"] = spot_manual
                    st.session_state["ibkr_chain"] = chain_manual
                    st.session_state["ibkr_exps"] = exps_manual
                    st.session_state.pop("ibkr_from_image", None)
                    st.session_state.pop("ibkr_img_bytes", None)
                    for k in list(st.session_state.keys()):
                        if k.startswith("ibkr_leg_"):
                            st.session_state.pop(k, None)
                    st.rerun()
            else:
                st.markdown("**Estrategia estándar**")
                opts = ["(elegir estrategia)"] + list(_ESTR_NOMBRES.keys())
                estrategia_sel = st.selectbox(
                    "Estrategia", opts, index=0,
                    format_func=lambda x: _ESTR_NOMBRES.get(x, x), key="ibkr_estr_sel",
                )

                if estrategia_sel != "(elegir estrategia)":
                    sp = 0.05
                    atm = _closest_strike(strikes_manual, spot_manual)
                    otm_c1 = _closest_strike(strikes_manual, spot_manual * (1 + sp))
                    otm_c2 = _closest_strike(strikes_manual, spot_manual * (1 + sp * 2))
                    otm_p1 = _closest_strike(strikes_manual, spot_manual * (1 - sp))
                    otm_p2 = _closest_strike(strikes_manual, spot_manual * (1 - sp * 2))

                    if estrategia_sel in ("straddle", "short_straddle", "covered_call", "protective_put"):
                        K1 = st.selectbox("K", options=strikes_manual,
                                          index=strikes_manual.index(atm) if atm in strikes_manual else 0,
                                          key="ibkr_estr_K")
                        estr_kwargs = {"K": float(K1)}
                    elif estrategia_sel in ("strangle", "short_strangle", "combo", "collar", "box",
                                            "bull_call_spread", "bear_call_spread", "bull_put_spread", "bear_put_spread"):
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            K1 = st.selectbox("K1", options=strikes_manual,
                                              index=strikes_manual.index(otm_p1) if otm_p1 in strikes_manual else 0,
                                              key="ibkr_estr_K1")
                        with ec2:
                            K2 = st.selectbox("K2", options=strikes_manual,
                                              index=strikes_manual.index(otm_c1) if otm_c1 in strikes_manual else 1,
                                              key="ibkr_estr_K2")
                        estr_kwargs = {"K1": float(K1), "K2": float(K2)}
                    elif estrategia_sel == "ratio_spread":
                        ec1, ec2, ec3, ec4 = st.columns(4)
                        idx_k1 = strikes_manual.index(atm) if atm in strikes_manual else 0
                        idx_k2 = strikes_manual.index(otm_c1) if otm_c1 in strikes_manual else min(idx_k1 + 1, len(strikes_manual) - 1)
                        with ec1:
                            K1 = st.selectbox("K1", options=strikes_manual, index=idx_k1, key="ibkr_estr_K1")
                        with ec2:
                            K2 = st.selectbox("K2", options=strikes_manual, index=idx_k2, key="ibkr_estr_K2")
                        with ec3: n1 = st.number_input("n1", value=1, min_value=1, key="ibkr_estr_n1")
                        with ec4: n2 = st.number_input("n2", value=2, min_value=1, key="ibkr_estr_n2")
                        estr_kwargs = {"K1": float(K1), "K2": float(K2), "n1": int(n1), "n2": int(n2)}
                    elif estrategia_sel in ("call_butterfly", "put_butterfly", "iron_butterfly"):
                        ec1, ec2, ec3 = st.columns(3)
                        with ec1:
                            K1 = st.selectbox("K1", options=strikes_manual,
                                              index=strikes_manual.index(otm_p1) if otm_p1 in strikes_manual else 0,
                                              key="ibkr_estr_K1")
                        with ec2:
                            K2 = st.selectbox("K2", options=strikes_manual,
                                              index=strikes_manual.index(atm) if atm in strikes_manual else len(strikes_manual)//2,
                                              key="ibkr_estr_K2")
                        with ec3:
                            K3 = st.selectbox("K3", options=strikes_manual,
                                              index=strikes_manual.index(otm_c1) if otm_c1 in strikes_manual else -1,
                                              key="ibkr_estr_K3")
                        estr_kwargs = {"K1": float(K1), "K2": float(K2), "K3": float(K3)}
                    else:
                        ec1, ec2, ec3, ec4 = st.columns(4)
                        idx_p2 = strikes_manual.index(otm_p2) if otm_p2 in strikes_manual else 0
                        idx_p1 = strikes_manual.index(otm_p1) if otm_p1 in strikes_manual else min(1, len(strikes_manual)-1)
                        idx_c1 = strikes_manual.index(otm_c1) if otm_c1 in strikes_manual else min(len(strikes_manual)-2, len(strikes_manual)//2)
                        idx_c2 = strikes_manual.index(otm_c2) if otm_c2 in strikes_manual else len(strikes_manual)-1
                        with ec1: K1 = st.selectbox("K1", options=strikes_manual, index=idx_p2, key="ibkr_estr_K1")
                        with ec2: K2 = st.selectbox("K2", options=strikes_manual, index=idx_p1, key="ibkr_estr_K2")
                        with ec3: K3 = st.selectbox("K3", options=strikes_manual, index=idx_c1, key="ibkr_estr_K3")
                        with ec4: K4 = st.selectbox("K4", options=strikes_manual, index=idx_c2, key="ibkr_estr_K4")
                        estr_kwargs = {"K1": float(K1), "K2": float(K2), "K3": float(K3), "K4": float(K4)}

                    if estrategia_sel in ("covered_call", "protective_put"):
                        st.caption("⚠️ Recordá poner cantidad de acciones en 'Stock' si aplica.")

                    if st.button("Cargar estrategia", key="ibkr_manual_load_estr"):
                        piernas = ESTRATEGIA_PIERNAS[estrategia_sel](**estr_kwargs)
                        legs = []
                        for tipo, K, coef in piernas:
                            action = "comprar" if coef > 0 else "vender"
                            leg = {
                                "action": action, "type": "call" if tipo == "C" else "put",
                                "expiry": exp_str, "strike": int(K), "quantity": int(coef),
                                "ultimo": None, "ultimo_last": None, "ultimo_mid": None,
                                "ultimo_bid": None, "ultimo_ask": None,
                                "sigma": 0.25, "precio_compra": 0.0,
                            }
                            bid, ask, last = _bid_ask_last_from_chain(chain_manual, float(K), leg["type"], exp_str)
                            if bid is not None: leg["ultimo_bid"] = round(float(bid), 3)
                            if ask is not None: leg["ultimo_ask"] = round(float(ask), 3)
                            if last is not None: leg["ultimo_last"] = round(float(last), 3)
                            if bid is not None and ask is not None: leg["ultimo_mid"] = round((bid + ask) / 2, 3)
                            leg["ultimo"] = leg.get("ultimo_last") or leg.get("ultimo_mid") or leg.get("ultimo_bid") or leg.get("ultimo_ask")
                            legs.append(leg)
                        st.session_state["ibkr_parsed"] = {"ticker": ticker_manual, "legs": legs, "posicion_info": {}}
                        st.session_state["ibkr_ticker"] = ticker_manual
                        st.session_state["_ibkr_spot_update"] = spot_manual
                        st.session_state["ibkr_chain"] = chain_manual
                        st.session_state["ibkr_exps"] = exps_manual
                        st.session_state.pop("ibkr_from_image", None)
                        st.session_state.pop("ibkr_img_bytes", None)
                        for k in list(st.session_state.keys()):
                            if k.startswith("ibkr_leg_"):
                                st.session_state.pop(k, None)
                        st.rerun()
                else:
                    st.info("Elegí una estrategia y hacé clic en **Cargar estrategia**.")

    if not st.session_state.get("ibkr_parsed"):
        st.stop()

# ── Rama Foto: file_uploader + OCR automático ──────────────────────────────────
else:
    uploaded = st.file_uploader(
        "Subir captura IBKR",
        type=["png", "jpg", "jpeg", "webp"],
        help="Captura de estrategia o cotización desde la app IBKR. OCR se ejecuta automáticamente.",
        key="ibkr_upload",
    )

    if uploaded:
        img_bytes = uploaded.read()
        if not st.session_state.get("ibkr_parsed"):
            with st.spinner("Extrayendo texto con OCR (puede tardar la primera vez)..."):
                ocr_error = None
                try:
                    from PIL import Image
                    import easyocr
                    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    img_np = np.array(img)
                    reader = easyocr.Reader(["en", "es"], gpu=False, verbose=False)
                    results = reader.readtext(img_np)
                    sorted_results = sorted(results, key=lambda r: (
                        (r[0][0][1] + r[0][2][1]) / 2, (r[0][0][0] + r[0][2][0]) / 2
                    ))
                    ocr_text = " ".join(t for (_, t, _) in sorted_results)
                    st.session_state["ibkr_ocr_raw"] = ocr_text
                    _webapp = Path(__file__).resolve().parent.parent
                    if str(_webapp) not in sys.path:
                        sys.path.insert(0, str(_webapp))
                    from ibkr_ocr_parser import parse_ibkr_ocr
                    data = parse_ibkr_ocr(ocr_text, mode=ibkr_mode)
                    st.session_state["ibkr_parsed"] = data
                    st.session_state["ibkr_ticker"] = (data.get("ticker", "") or "").strip().upper() or "UNKNOWN"
                    st.session_state["ibkr_from_image"] = True
                    st.session_state["ibkr_img_bytes"] = img_bytes
                    for k in list(st.session_state.keys()):
                        if k.startswith("ibkr_leg_"):
                            st.session_state.pop(k, None)
                    st.rerun()
                except ImportError as e:
                    ocr_error = f"Falta instalar EasyOCR: `pip install easyocr`\n\nError: {e}"
                except Exception as e:
                    ocr_error = str(e)
                    st.session_state["ibkr_parsed"] = {
                        "ticker": "UNKNOWN", "legs": [_empty_leg()], "posicion_info": {},
                    }
                    st.session_state["ibkr_ticker"] = "UNKNOWN"
                    st.session_state["ibkr_from_image"] = True
                    st.session_state["ibkr_img_bytes"] = img_bytes
                    for k in list(st.session_state.keys()):
                        if k.startswith("ibkr_leg_"):
                            st.session_state.pop(k, None)
                    st.warning("No se pudo leer la imagen. Completá los campos manualmente.")
                    if ocr_error:
                        st.error(ocr_error)
                    st.rerun()

        st.image(img_bytes, width=220, caption="Vista previa")
        if st.button("🗑️ Borrar imagen", key="ibkr_borrar_img"):
            for k in list(st.session_state.keys()):
                if k.startswith("ibkr_"):
                    st.session_state.pop(k, None)
            st.rerun()

    if not st.session_state.get("ibkr_parsed"):
        st.caption("Subí una captura, o cargá una posición guardada.")
        st.stop()

# ════════════════════════════════════════════════════════════════════════════
# EDITOR DE POSICIÓN
# ════════════════════════════════════════════════════════════════════════════

data     = st.session_state["ibkr_parsed"]
legs_raw = data.get("legs", [])
if not legs_raw:
    legs_raw = [_empty_leg()]
    st.session_state["ibkr_parsed"]["legs"] = legs_raw

# Aplicar actualizaciones de IV antes de renderizar widgets
if "_ibkr_iv_updates" in st.session_state:
    for i, iv_val in st.session_state["_ibkr_iv_updates"].items():
        st.session_state[f"ibkr_leg_{i}_sigma_pct"] = round(iv_val * 100, 2)
    st.session_state.pop("_ibkr_iv_updates", None)
if "_ibkr_spot_update" in st.session_state:
    st.session_state["ibkr_spot"] = st.session_state.pop("_ibkr_spot_update")

col_foto, col_info = st.columns([1, 1])
with col_foto:
    st.markdown("**Captura**")
    if st.session_state.get("ibkr_img_bytes"):
        st.image(st.session_state["ibkr_img_bytes"], width=330)
    else:
        st.caption("(sin imagen — entrada manual)")

with col_info:
    st.markdown("**Información** *(editable)*")
    if "ibkr_ticker" not in st.session_state:
        st.session_state["ibkr_ticker"] = (data.get("ticker", "") or "").strip().upper() or "UNKNOWN"
    ticker = st.text_input("Ticker", key="ibkr_ticker").strip().upper() or "UNKNOWN"
    st.session_state["ibkr_parsed"]["ticker"] = ticker

    # Spot
    if ticker and ticker != "UNKNOWN":
        try:
            from Codigo.data.market_data import get_spot as _get_spot_fn
            _spot_fetched = _get_spot_fn(ticker)
        except Exception:
            _spot_fetched = None
    else:
        _spot_fetched = None
    spot_default = st.session_state.get("ibkr_spot") if "ibkr_spot" in st.session_state else (_spot_fetched or 0.0)
    spot = st.number_input("Precio hoy", value=float(spot_default), min_value=0.0,
                           step=0.01, format="%.2f", key="ibkr_spot")

    # ── Legs ─────────────────────────────────────────────────────────────────
    legs_edited = []
    for i, leg in enumerate(legs_raw):
        action       = str(leg.get("action", "comprar")).lower()
        side_default = "Long" if "comprar" in action or "buy" in action else "Short"
        qty_raw      = int(leg.get("quantity", 1))
        pc_default   = float(leg.get("precio_compra", leg.get("price_paid", 0)) or 0)

        st.markdown(f"**Opción {i+1}**")
        row_a, row_del = st.columns([10, 1])
        with row_del:
            st.write("")
            if st.button("🗑️", key=f"ibkr_del_leg_{i}", help="Quitar este leg"):
                st.session_state["ibkr_parsed"]["legs"].pop(i)
                for k in list(st.session_state.keys()):
                    if k.startswith(f"ibkr_leg_{i}_"):
                        st.session_state.pop(k, None)
                st.rerun()

        c1, c2, c3 = st.columns(3)
        with c1:
            side = st.selectbox("L/S", ["Long", "Short"],
                                index=0 if "long" in side_default.lower() else 1,
                                key=f"ibkr_leg_{i}_side")
        with c2:
            opt_type = st.selectbox("Tipo", ["call", "put"],
                                    index=0 if "call" in str(leg.get("type", "call")).lower() else 1,
                                    key=f"ibkr_leg_{i}_type")
        with c3:
            qty_abs = st.number_input("Cantidad", value=abs(qty_raw), min_value=1,
                                      key=f"ibkr_leg_{i}_qty")
        qty = qty_abs if side == "Long" else -qty_abs

        c4, c5 = st.columns(2)
        with c4:
            strike = st.number_input("Strike", value=int(leg.get("strike", 0)),
                                     min_value=1, key=f"ibkr_leg_{i}_strike")
        with c5:
            expiry = st.text_input("Expiry (YYYY-MM-DD)",
                                   value=str(leg.get("expiry", ""))[:10],
                                   key=f"ibkr_leg_{i}_expiry")

        # Precio de mercado (bid/ask/last/mid) — elegir cuál usar
        ultimo_bid  = leg.get("ultimo_bid")
        ultimo_ask  = leg.get("ultimo_ask")
        ultimo_last = leg.get("ultimo_last")
        ultimo_mid  = leg.get("ultimo_mid")
        ultimo_val  = leg.get("ultimo")
        price_opts = []
        if ultimo_bid is not None: price_opts.append(("bid", ultimo_bid, f"Bid: {ultimo_bid:.2f}"))
        if ultimo_ask is not None: price_opts.append(("ask", ultimo_ask, f"Ask: {ultimo_ask:.2f}"))
        if ultimo_last is not None: price_opts.append(("last", ultimo_last, f"Last: {ultimo_last:.2f}"))
        if ultimo_mid is not None: price_opts.append(("mid", ultimo_mid, f"Mid: {ultimo_mid:.2f}"))
        if price_opts:
            choice_keys = [p[0] for p in price_opts]
            default_idx = 0
            for pref in ("last", "mid", "bid", "ask"):
                if pref in choice_keys:
                    default_idx = choice_keys.index(pref)
                    break
            ultimo_choice = st.radio(
                "Precio de mercado (usar)",
                options=choice_keys,
                format_func=lambda x: next((p[2] for p in price_opts if p[0] == x), x),
                index=default_idx,
                key=f"ibkr_leg_{i}_ultimo_choice", horizontal=True,
            )
            ultimo_default = next((p[1] for p in price_opts if p[0] == ultimo_choice), ultimo_val or 0.0)
            ultimo_key = f"ibkr_leg_{i}_ultimo_{ultimo_choice}"
        else:
            ultimo_default = float(ultimo_val) if ultimo_val is not None else 0.0
            ultimo_key = f"ibkr_leg_{i}_ultimo"
        ultimo = st.number_input("Precio (valor actual)", value=float(ultimo_default),
                                 min_value=0.0, step=0.01, format="%.2f", key=ultimo_key)

        # Precio pagado por leg
        pc_key = f"ibkr_leg_{i}_pagado"
        if pc_key not in st.session_state:
            st.session_state[pc_key] = pc_default
        precio_pagado_leg = st.number_input(
            "Precio pagado (por opción)", value=float(st.session_state[pc_key]),
            min_value=0.0, step=0.01, format="%.2f", key=pc_key,
            help="Prima que pagaste por esta opción al abrir la posición."
        )

        # IV en %
        _key_pct = f"ibkr_leg_{i}_sigma_pct"
        leg_sigma = float(leg.get("sigma", 0.25)) or 0.25
        if _key_pct not in st.session_state:
            st.session_state[_key_pct] = round(leg_sigma * 100, 2)
        sig_col, iv_btn_col = st.columns([2, 1])
        with sig_col:
            sigma_pct = st.number_input("IV %", min_value=1.0, max_value=300.0, step=0.5,
                                        format="%.1f", key=_key_pct)
            sigma = sigma_pct / 100.0
        with iv_btn_col:
            st.write("")
            if st.button("Calcular IV", key=f"ibkr_calc_iv_{i}"):
                pm_for_iv = ultimo
                if pm_for_iv > 0 and spot > 0:
                    try:
                        from Codigo.analytics.vol_implicita import impvolfunc_bs
                        exp_str  = str(expiry.strip()[:10])
                        exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
                        T_leg    = max((exp_date - datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0)).days, 1) / 365.0
                        _r   = st.session_state.get("ibkr_r", 0.05)
                        _div = st.session_state.get("ibkr_div", 0.0)
                        _tp  = "C" if opt_type == "call" else "P"
                        iv   = impvolfunc_bs(_tp, spot, float(strike), T_leg, _r, pm_for_iv, _div)
                        st.session_state["_ibkr_iv_updates"] = {i: round(iv, 4)}
                        st.session_state.pop("ibkr_esc_cached", None)
                        st.session_state.pop("ibkr_esc_params", None)
                        st.session_state.pop("ibkr_esc_result", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"IV: {e}")
                else:
                    st.warning("Precio hoy y Último > 0 para calcular IV")

        legs_edited.append({
            "side": side, "type": opt_type,
            "strike": strike, "expiry": expiry.strip()[:10],
            "qty": qty, "ultimo": ultimo,
            "precio_pagado": precio_pagado_leg,
            "sigma": sigma,
        })
        st.markdown("---")

    # Agregar / quitar legs
    add_col, _ = st.columns([1, 3])
    with add_col:
        if st.button("➕ Agregar opción", key="ibkr_add_leg"):
            st.session_state["ibkr_parsed"]["legs"].append(_empty_leg())
            st.rerun()

    # Persistir ediciones
    if legs_edited and "legs" in st.session_state["ibkr_parsed"]:
        for i, ed in enumerate(legs_edited):
            if i < len(st.session_state["ibkr_parsed"]["legs"]):
                st.session_state["ibkr_parsed"]["legs"][i].update({
                    "action": "comprar" if ed["qty"] > 0 else "vender",
                    "quantity": ed["qty"],
                    "type": ed["type"],
                    "strike": ed["strike"],
                    "expiry": ed["expiry"],
                    "ultimo": ed["ultimo"],
                    "sigma": ed["sigma"],
                    "precio_compra": ed["precio_pagado"],
                })

    if legs_edited:
        iv_col, fetch_col = st.columns([1, 1])
        with iv_col:
            if st.button("Calcular IV (todas las opciones)", key="ibkr_calc_iv_all"):
                try:
                    from Codigo.analytics.vol_implicita import impvolfunc_bs
                    _r = st.session_state.get("ibkr_r", 0.05)
                    _div = st.session_state.get("ibkr_div", 0.0)
                    updates = {}
                    for i, leg in enumerate(legs_edited):
                        pm = leg.get("ultimo", 0)
                        if pm <= 0:
                            continue
                        exp_str = str(leg.get("expiry", ""))[:10]
                        try:
                            exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
                        except Exception:
                            continue
                        T_leg = max((exp_date - datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0)).days, 1) / 365.0
                        _tp = "C" if leg.get("type") == "call" else "P"
                        iv  = impvolfunc_bs(_tp, spot, float(leg.get("strike", 0)), T_leg, _r, pm, _div)
                        updates[i] = round(iv, 4)
                    st.session_state["_ibkr_iv_updates"] = updates
                    st.session_state.pop("ibkr_esc_cached", None)
                    st.session_state.pop("ibkr_esc_params", None)
                    st.session_state.pop("ibkr_esc_result", None)
                    st.rerun()
                except Exception as e:
                    st.error(f"IV: {e}")
        with fetch_col:
            if st.button("Traer bid/ask/last de mercado", key="ibkr_fetch_market"):
                _tk = st.session_state.get("ibkr_ticker", "").strip().upper()
                if not _tk or _tk == "UNKNOWN":
                    st.warning("Ingresá un ticker válido primero.")
                else:
                    _orig_stderr = sys.stderr
                    try:
                        sys.stderr = open(os.devnull, "w", encoding="utf-8")
                    except Exception:
                        pass
                    try:
                        with st.spinner(f"Buscando precios de {_tk}..."):
                            from Codigo.data.market_data import get_spot, get_options_chain
                            chain = get_options_chain(_tk, None)
                            spot_new = get_spot(_tk)
                            st.session_state["_ibkr_spot_update"] = spot_new
                            st.session_state["ibkr_chain"] = chain
                            legs_to_update = st.session_state["ibkr_parsed"].get("legs", [])
                            for i, leg in enumerate(legs_to_update):
                                bid, ask, last = _bid_ask_last_from_chain(
                                    chain, leg.get("strike"), leg.get("type"), leg.get("expiry", "")
                                )
                                leg["ultimo_bid"] = round(float(bid), 3) if bid is not None else None
                                leg["ultimo_ask"] = round(float(ask), 3) if ask is not None else None
                                leg["ultimo_last"] = round(float(last), 3) if last is not None else None
                                mid = round((bid + ask) / 2, 3) if bid is not None and ask is not None else None
                                leg["ultimo_mid"] = mid
                                leg["ultimo"] = last if last is not None else (mid if mid is not None else (bid if bid is not None else ask))
                                for k in list(st.session_state.keys()):
                                    if k.startswith(f"ibkr_leg_{i}_ultimo"):
                                        st.session_state.pop(k, None)
                            st.session_state.pop("ibkr_esc_cached", None)
                            st.session_state.pop("ibkr_esc_params", None)
                            st.session_state.pop("ibkr_esc_result", None)
                            st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo obtener datos: {e}")
                    finally:
                        try:
                            if sys.stderr != _orig_stderr:
                                sys.stderr.close()
                            sys.stderr = _orig_stderr
                        except Exception:
                            pass

    if st.session_state.get("ibkr_ocr_raw"):
        with st.expander("Texto OCR extraído", expanded=False):
            st.text(st.session_state["ibkr_ocr_raw"])

# ════════════════════════════════════════════════════════════════════════════
# CONSTRUIR legs para cálculos
# ════════════════════════════════════════════════════════════════════════════
    legs = []
    for leg in legs_edited:
        legs.append({
        "expiry":               str(leg.get("expiry", ""))[:10],
        "strike":               float(leg["strike"]),
        "type":                 leg["type"],
        "qty":                  leg["qty"],
        "precio_mercado":       float(leg.get("ultimo", 0)),
            "precio_mercado_source": "last",
        "precio_pagado":        float(leg.get("precio_pagado", 0)),
        "sigma":                float(leg.get("sigma", 0.25)),
    })

# ── Tabla resumen ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Estrategia para valuar")
rows_sum = []
for i, lg in enumerate(legs):
    side = "Long" if lg["qty"] > 0 else "Short"
    rows_sum.append({
        "Leg": i + 1, "L/S": side,
        "Tipo": lg["type"].upper(), "Strike": lg["strike"],
        "Expiry": lg["expiry"], "Cant": abs(lg["qty"]),
        "Último": f"${lg['precio_mercado']:.2f}",
        "Pagado": f"${lg['precio_pagado']:.2f}",
        "IV %": round(lg["sigma"] * 100, 1),
        "Valor hoy": round(lg["qty"] * LOTES * lg["precio_mercado"], 2),
    })
if rows_sum:
    st.dataframe(pd.DataFrame(rows_sum).set_index("Leg"), use_container_width=True,
                 height=min(220, 75 + len(rows_sum) * 35))

# ── Botones acción ────────────────────────────────────────────────────────────
ac1, ac2 = st.columns(2)
with ac1:
        cargar_md = st.button("Cargar datos de mercado", type="primary", key="go_mdp")
with ac2:
    if st.button("Limpiar y empezar de nuevo", key="clear_ibkr"):
        for k in list(st.session_state.keys()):
            if k.startswith("ibkr_"):
                st.session_state.pop(k, None)
            st.rerun()

    with st.expander("💾 Guardar posición", expanded=False):
        pos_name = st.text_input("Nombre", value=f"{ticker} {datetime.now().strftime('%Y-%m-%d')}",
                                 key="ibkr_save_name")
        if st.button("Guardar posición", key="ibkr_save_btn"):
            _save_ibkr_position(pos_name, ticker, legs)
            st.success(f"Posición guardada: {pos_name or ticker}")

    if cargar_md and ticker and ticker != "UNKNOWN":
        _orig_stderr = sys.stderr
        try:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")
        except Exception:
            pass
        try:
            with st.spinner(f"Cargando {ticker}..."):
                from Codigo.data.market_data import get_spot, get_expirations, get_options_chain
                try:
                    from Codigo.data.market_data import get_dividend_yield, get_risk_free_rate, get_implied_vol_atm
                except ImportError:
                    get_dividend_yield = lambda t: 0.0
                    get_risk_free_rate = lambda: 0.05
                    get_implied_vol_atm = lambda df, s, e: None
                spot_new = get_spot(ticker)
                st.session_state["_ibkr_spot_update"] = spot_new
                exps = get_expirations(ticker)
                st.session_state["ibkr_exps"] = exps
                div = get_dividend_yield(ticker)
                st.session_state["ibkr_div"] = round(div, 4)
                r_pct = get_risk_free_rate()
                st.session_state["ibkr_r"] = round(r_pct, 4)
                if exps:
                    chain_df_new = get_options_chain(ticker, None)
                    st.session_state["ibkr_chain"] = chain_df_new
                    sigma_atm = get_implied_vol_atm(chain_df_new, spot_new, exps[-1])
                    st.session_state["ibkr_sigma"] = round(sigma_atm, 4) if sigma_atm else 0.25
                else:
                    st.session_state["ibkr_sigma"] = 0.25
                st.session_state["ibkr_legs"] = legs
                st.session_state.pop("ibkr_error", None)
        except Exception as e:
            st.session_state["ibkr_error"] = str(e)
        finally:
            try:
                if sys.stderr != _orig_stderr:
                    sys.stderr.close()
                sys.stderr = _orig_stderr
            except Exception:
                pass
        st.rerun()

    if st.session_state.get("ibkr_error"):
        st.error(st.session_state["ibkr_error"])

if not (st.session_state.get("ibkr_spot") and legs):
    st.info("Cargá datos de mercado para ver Resumen, Griegas, Payoff y Escenarios.")
    st.stop()

spot = float(st.session_state["ibkr_spot"])

# ════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Resumen")

valor_opciones   = sum(int(lg["qty"]) * LOTES * float(lg["precio_mercado"]) for lg in legs)
pagado_por_legs  = sum(int(lg["qty"]) * LOTES * float(lg["precio_pagado"]) for lg in legs)

r1, r2, r3 = st.columns(3)
with r1:
    st.metric("Mercado HOY", f"${valor_opciones:,.2f}")
with r2:
    st.metric("Pagado (Σ legs)", f"${pagado_por_legs:,.2f}")
with r3:
    pnl_hoy = valor_opciones - pagado_por_legs
    color = "#dc3545" if pnl_hoy < 0 else "#28a745"
    st.markdown("**P&L actual**")
    st.markdown(f'<span style="color:{color}; font-size:1.4rem; font-weight:700;">${pnl_hoy:+,.2f}</span>',
                unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PARÁMETROS r / div
# ════════════════════════════════════════════════════════════════════════════
_r_default   = st.session_state.get("ibkr_r",   0.05)
_div_default = st.session_state.get("ibkr_div", 0.0)
st.session_state.setdefault("ibkr_esc_r",   _r_default)
st.session_state.setdefault("ibkr_esc_div", _div_default)

def _fetch_r_subprocess():
    script = _WEBAPP_DIR / "_fetch_r.py"
    try:
        out = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                             timeout=20, cwd=_PROJECT_ROOT)
        if out.returncode == 0 and out.stdout.strip():
            val_str, src = out.stdout.strip().split("|", 1)
            return float(val_str), src
    except Exception:
        pass
    return None

if st.session_state.get("_ibkr_calc_r_pending"):
    st.session_state.pop("_ibkr_calc_r_pending", None)
    result = _fetch_r_subprocess()
    if result:
        r_val, r_source = result
        st.session_state["ibkr_esc_r"]        = round(float(r_val), 4)
        st.session_state["ibkr_esc_r_source"] = r_source
    else:
        st.error("No se pudo obtener ^IRX")

# ════════════════════════════════════════════════════════════════════════════
# GRIEGAS DEL PORTFOLIO
# ════════════════════════════════════════════════════════════════════════════
        st.divider()
st.subheader("Griegas del portfolio")

r_g   = float(st.session_state.get("ibkr_esc_r",   _r_default))
div_g = float(st.session_state.get("ibkr_esc_div", _div_default))
today = datetime.now().date()

total_delta = total_gamma = total_vega = total_theta = 0.0
greek_rows = []
for lg in legs:
    K      = float(lg["strike"])
    qty    = int(lg["qty"])
    tp     = "C" if lg["type"] == "call" else "P"
    sig_l  = float(lg["sigma"]) or 0.25
    exp_s  = str(lg["expiry"])[:10]
    try:
        T_l = max((datetime.strptime(exp_s, "%Y-%m-%d").date() - today).days, 0) / 365.0
    except Exception:
        T_l = 0.25
    if spot > 0 and K > 0 and sig_l > 0:
        g    = _bs_greeks(tp, spot, K, T_l, r_g, sig_l, div_g)
        lote = qty * LOTES
        total_delta += lote * g["delta"]
        total_gamma += lote * g["gamma"]
        total_vega  += lote * g["vega"]
        total_theta += lote * g["theta"]
        greek_rows.append({
            "Leg": f"{tp} K={K:.0f}",
            "Qty×Lote": lote,
            "Δ": round(lote * g["delta"], 3),
            "Γ": round(lote * g["gamma"], 4),
            "ν": round(lote * g["vega"],  2),
            "Θ (día)": round(lote * g["theta"], 3),
        })

gg1, gg2, gg3, gg4 = st.columns(4)
with gg1: st.metric("Δ Delta",       f"{total_delta:+.3f}")
with gg2: st.metric("Γ Gamma",       f"{total_gamma:+.4f}")
with gg3: st.metric("ν Vega ($/1%)", f"{total_vega:+.2f}")
with gg4: st.metric("Θ Theta/día",   f"{total_theta:+.3f}")

with st.expander("Desglose por leg", expanded=False):
    df_g = pd.DataFrame(greek_rows)
    if not df_g.empty:
        total_row = pd.DataFrame([{
            "Leg": "TOTAL", "Qty×Lote": "—",
            "Δ": round(total_delta, 3), "Γ": round(total_gamma, 4),
            "ν": round(total_vega, 2), "Θ (día)": round(total_theta, 3),
        }])
        st.dataframe(pd.concat([df_g, total_row], ignore_index=True),
                     use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# PAYOFF / P&L AL VENCIMIENTO
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Payoff / P&L al vencimiento")

try:
    from Codigo.analytics.payoffs import payoff_call as _pcall, payoff_put as _pput
except ImportError:
    def _pcall(S, K): return max(float(S) - float(K), 0.0)
    def _pput(S, K):  return max(float(K) - float(S), 0.0)

# Rango inteligente basado en strikes
all_strikes  = [float(lg["strike"]) for lg in legs]
K_min        = min(all_strikes) if all_strikes else spot * 0.8
K_max        = max(all_strikes) if all_strikes else spot * 1.2
S_lo_pay     = K_min * 0.80
S_hi_pay     = K_max * 1.20

# T_max y costo FV
exp_dates_pay = []
for lg in legs:
    try:
        exp_dates_pay.append(datetime.strptime(str(lg["expiry"])[:10], "%Y-%m-%d").date())
    except Exception:
        pass
T_max_pay    = max((d - today).days for d in exp_dates_pay) / 365.0 if exp_dates_pay else 0.25
costo_fv     = pagado_por_legs * np.exp(r_g * T_max_pay) if pagado_por_legs != 0 else 0.0

S_pay = np.linspace(S_lo_pay, S_hi_pay, 400)
payoff_opts = np.zeros_like(S_pay)
for lg in legs:
    K   = float(lg["strike"]); qty = int(lg["qty"])
    if lg["type"] == "call":
        payoff_opts += qty * LOTES * np.maximum(S_pay - K, 0)
    else:
        payoff_opts += qty * LOTES * np.maximum(K - S_pay, 0)
pnl_pay   = payoff_opts - costo_fv
beps      = _find_breakevens(S_pay, pnl_pay)
mx_idx    = int(np.argmax(pnl_pay))
mn_idx    = int(np.argmin(pnl_pay))

fig_p, ax_p = plt.subplots(figsize=(11, 4.5), dpi=100)
ax_p.fill_between(S_pay, pnl_pay, 0, where=(pnl_pay >= 0), color="#28a745", alpha=0.18)
ax_p.fill_between(S_pay, pnl_pay, 0, where=(pnl_pay <  0), color="#dc3545", alpha=0.18)
ax_p.plot(S_pay, payoff_opts, "--", color="#888", linewidth=1.4, label="Payoff (sin costo)")
ax_p.plot(S_pay, pnl_pay, color="#1f77b4", linewidth=2.2,
          label=f"P&L (costo FV = ${costo_fv:,.0f})")
ax_p.axhline(0, color="black", linewidth=0.7)
if S_lo_pay <= spot <= S_hi_pay:
    ax_p.axvline(spot, color="#2ca02c", linewidth=1.3, linestyle="--", alpha=0.9,
                 label=f"Spot = {spot:.2f}")
for K in sorted(set(all_strikes)):
    ax_p.axvline(K, color="#ff7f0e", linewidth=0.9, linestyle=":", alpha=0.7, label=f"K={K:.0f}")
for be in beps:
    ax_p.axvline(be, color="#9467bd", linewidth=1.1, linestyle="--", alpha=0.75)
    ax_p.annotate(f"BE\n${be:.2f}", xy=(be, 0),
                  xytext=(be, (pnl_pay.max() - pnl_pay.min()) * 0.07),
                  fontsize=7.5, ha="center", color="#9467bd",
                  arrowprops=dict(arrowstyle="-", color="#9467bd", lw=0.8))
ax_p.axhline(pnl_pay[mx_idx], color="#28a745", linewidth=0.9, linestyle=":", alpha=0.7)
ax_p.axhline(pnl_pay[mn_idx], color="#dc3545", linewidth=0.9, linestyle=":", alpha=0.7)
ax_p.set_xlabel("Precio del subyacente S", fontsize=10)
ax_p.set_ylabel("P&L ($)", fontsize=10)
ax_p.set_title(f"P&L al vencimiento — {ticker}", fontsize=11)
handles, labels_h = ax_p.get_legend_handles_labels()
seen_p = {}
for h, lb in zip(handles, labels_h):
    if lb not in seen_p:
        seen_p[lb] = h
ax_p.legend(seen_p.values(), seen_p.keys(), fontsize=8)
ax_p.grid(True, alpha=0.2)
plt.tight_layout()
st.pyplot(fig_p, use_container_width=True)
plt.close(fig_p)

st.markdown("**Resumen del P&L**")
st.dataframe(pd.DataFrame({
    "Concepto": ["Máxima ganancia", "Máxima pérdida", "Break-even(s)", "Costo pagado (FV)"],
    "Valor ($)": [
        f"${pnl_pay[mx_idx]:,.2f}" if not np.isinf(pnl_pay[mx_idx]) else "Ilimitada",
        f"${pnl_pay[mn_idx]:,.2f}" if not np.isinf(abs(pnl_pay[mn_idx])) else "Ilimitada",
        ", ".join([f"${b}" for b in beps]) if beps else "—",
        f"${costo_fv:,.2f}",
    ],
    "Nivel S": [f"${S_pay[mx_idx]:.2f}", f"${S_pay[mn_idx]:.2f}", "—", "—"],
}), use_container_width=True, hide_index=True)
st.caption(f"P&L = Payoff − FV(pagado) = Payoff − ${pagado_por_legs:,.2f} × e^({r_g:.4f}×{T_max_pay:.3f})")

# ════════════════════════════════════════════════════════════════════════════
# ESCENARIOS
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("Escenarios")

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


# Grilla
st.markdown("**Grilla**")
eg1, eg2, eg3, eg4 = st.columns(4)
with eg1:
    n_cols = st.number_input("Columnas (tiempo)", value=4, min_value=2, max_value=20, step=1, key="ibkr_esc_ncol")
with eg2:
    n_rows = st.number_input("Filas (precio)", value=11, min_value=3, max_value=51, step=2, key="ibkr_esc_nrow")
with eg3:
    S_desde = st.number_input("S desde", value=round(S_lo_pay, 1), min_value=0.1, step=1.0, format="%.1f", key="ibkr_esc_s_desde")
with eg4:
    S_a = st.number_input("S hasta", value=round(S_hi_pay, 1), min_value=0.1, step=1.0, format="%.1f", key="ibkr_esc_s_a")

# Parámetros
st.markdown("**Parámetros**")
ep1, ep2 = st.columns(2)
with ep1:
    st.markdown("r (^IRX)")
    r_row = st.columns([1, 0.35])
    with r_row[0]:
        r = st.number_input("r", value=float(st.session_state["ibkr_esc_r"]),
                            format="%.4f", step=0.001, key="ibkr_esc_r_val", label_visibility="collapsed")
        st.session_state["ibkr_esc_r"] = r
    with r_row[1]:
        if st.button("Calcular", key="ibkr_calc_r"):
            st.session_state["_ibkr_calc_r_pending"] = True
            st.rerun()
    if st.session_state.get("ibkr_esc_r_source"):
        st.caption(f"✓ {st.session_state.get('ibkr_esc_r_source','?')} → {r*100:.2f}%")
with ep2:
    st.markdown("div (dividendYield)")
    d_row = st.columns([1, 0.35])
    with d_row[0]:
        div = st.number_input("div", value=float(st.session_state["ibkr_esc_div"]),
                              format="%.4f", step=0.001, key="ibkr_esc_div_val", label_visibility="collapsed")
        st.session_state["ibkr_esc_div"] = div
    with d_row[1]:
        def _calc_div_ibkr():
            _tk = st.session_state.get("ibkr_ticker", "") or ""
            if _tk and _tk != "UNKNOWN":
                try:
                    from Codigo.data.market_data import get_dividend_yield
                    dv = get_dividend_yield(_tk)
                    st.session_state["ibkr_esc_div"] = round(dv, 4)
                    st.session_state["ibkr_esc_div_source"] = "dividendYield"
                except Exception:
                    pass
        if st.button("Calcular", key="ibkr_calc_div", on_click=_calc_div_ibkr):
            if st.session_state.get("ibkr_ticker", "") in ("", "UNKNOWN"):
                st.warning("Cargá ticker primero.")
        if st.session_state.get("ibkr_esc_div_source"):
            st.caption(f"✓ {st.session_state.get('ibkr_esc_div_source','?')} → {div*100:.2f}%")

# Modelo
st.markdown("**Modelo**")
em1, em2, em3 = st.columns(3)
with em1:
    modelo = st.selectbox("Modelo", ["BAW", "Binomial", "Monte Carlo", "Diferencias finitas"],
                          index=0, key="ibkr_esc_modelo")
with em2:
    pasos = st.number_input("Pasos", value=100, min_value=10, max_value=500, step=50,
                            key="ibkr_esc_pasos", disabled=(modelo not in ("Binomial", "Monte Carlo")))
with em3:
    M_fd = st.number_input("M (FD)", value=150, min_value=20, max_value=500, step=10,
                           key="ibkr_esc_M", disabled=(modelo != "Diferencias finitas"))

# Invalidar caché si cambiaron parámetros
_ibkr_esc_params = (
    n_rows, n_cols, S_desde, S_a, modelo, pasos, M_fd, r, div,
    tuple((lg.get("strike"), lg.get("qty"), str(lg.get("expiry", "")), str(lg.get("type", "")), lg.get("sigma"), float(lg.get("precio_pagado", 0) or 0)) for lg in legs),
)
_ibkr_stored_params = st.session_state.get("ibkr_esc_params")
if _ibkr_stored_params is not None and _ibkr_esc_params != _ibkr_stored_params:
    st.session_state.pop("ibkr_esc_cached", None)
    st.session_state.pop("ibkr_esc_params", None)
    st.session_state.pop("ibkr_esc_result", None)

calc_esc = st.button(
    "Recalcular escenarios" if st.session_state.get("ibkr_esc_cached") else "Calcular escenarios",
    type="primary", key="ibkr_calc_esc",
)
if calc_esc:
    st.session_state["ibkr_esc_cached"] = True
    st.session_state.pop("ibkr_esc_result", None)

if not st.session_state.get("ibkr_esc_cached"):
    st.info("Hacé clic en **Calcular escenarios** para ver la matriz.")
    st.stop()

# ── Usar resultado cacheado si existe ─────────────────────────────────────────
mat = df_esc = df_pnl = date_cols = unique_cols = row_labels = n_cols_actual = None
if _ibkr_stored_params is not None and _ibkr_esc_params == _ibkr_stored_params:
    _cached = st.session_state.get("ibkr_esc_result")
    if _cached is not None:
        mat, df_esc, df_pnl, date_cols, unique_cols, row_labels, n_cols_actual = _cached

if mat is None:
    # ── Build matrix ──────────────────────────────────────────────────────────
    expiry_dates_sc = []
    for lg in legs:
        try:
            expiry_dates_sc.append(pd.to_datetime(str(lg["expiry"])[:10]).date())
        except Exception:
            pass
    expiry_date  = max(expiry_dates_sc) if expiry_dates_sc else today + timedelta(days=365)
    T_max_days   = max((expiry_date - today).days, 0)
    T_max        = T_max_days / 365.0

    S_vals   = np.linspace(min(S_desde, S_a), max(S_desde, S_a), int(n_rows))
    t_vals   = [T_max * (n_cols - 1 - i) / max(1, n_cols - 1) for i in range(n_cols)]
    if n_cols >= 2 and T_max / max(1, n_cols - 1) > 1e-6:
        t_vals = t_vals[:-1] + [T_max / max(1, n_cols - 1) * 0.5, 0.0]
    n_cols_actual = len(t_vals)

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

    def _leg_days_ibkr(e):
        try:
            d = pd.to_datetime(str(e)[:10]).date()
            return (d - today).days
        except Exception:
            return 0

    st.session_state["ibkr_esc_params"] = _ibkr_esc_params

    prog = st.progress(0, text="Calculando escenarios...")
    st.caption("Si tarda mucho, refrescá la página para cancelar.")
    mat = np.zeros((int(n_rows), n_cols_actual))
    total_cells = int(n_rows) * n_cols_actual
    cell_idx = 0
    for i, S in enumerate(S_vals):
        for j, T in enumerate(t_vals):
            opt_val = 0.0
            for lg in legs:
                K     = float(lg["strike"])
                qty   = int(lg["qty"])
                tp    = "C" if lg["type"] == "call" else "P"
                T_ld  = max(_leg_days_ibkr(lg["expiry"]), 0) / 365.0
                T_eff = T_ld - T_max + T
                sig_l = float(lg["sigma"]) or 0.25
                _p    = int(pasos) if modelo in ("Binomial", "Monte Carlo") else 100
                _M_l  = int(M_fd)  if modelo == "Diferencias finitas" else 150
                if T_eff <= 0:
                    p = float(_pcall(S, K) if tp == "C" else _pput(S, K))
                else:
                    p = _price_opt(tp, S, K, T_eff, r, sig_l, div, modelo, _p, _M_l)
                opt_val += qty * LOTES * p
            mat[i, j] = opt_val
            cell_idx += 1
            if total_cells > 0 and cell_idx % max(1, total_cells // 20) == 0:
                prog.progress(min(1.0, cell_idx / total_cells), text=f"Calculando... {cell_idx}/{total_cells}")
    prog.progress(1.0, text="Listo")
    prog.empty()

    # Columnas e índice únicos (fix bug Styler)
    unique_cols = _unique_labels(date_cols)
    row_labels  = _unique_labels([f"S={s:.1f}" for s in S_vals])

    df_esc = pd.DataFrame(mat, index=row_labels, columns=unique_cols)
    df_esc = df_esc.iloc[::-1].round(1)
    df_pnl = (df_esc - pagado_por_legs).round(1)

    st.session_state["ibkr_esc_result"] = (mat, df_esc, df_pnl, date_cols, unique_cols, row_labels, n_cols_actual)


def _gradient_style(df, ref, fmt="{:.1f}"):
    v_min, v_max = df.values.min(), df.values.max()
    rng_neg = ref - v_min if v_min < ref else 1
    rng_pos = v_max - ref if v_max > ref else 1

    def _s(v):
        if pd.isna(v):
            return ""
        if v < ref:
            a = min(1, max(0, 0.2 + 0.6 * (ref - v) / rng_neg)) if rng_neg > 0 else 0.8
            return f"background-color:rgba(220,53,69,{a:.2f});color:{'#fff' if a>0.55 else '#1a1a1a'};font-weight:500"
        elif v > ref:
            a = min(1, max(0, 0.2 + 0.6 * (v - ref) / rng_pos)) if rng_pos > 0 else 0.8
            return f"background-color:rgba(40,167,69,{a:.2f});color:{'#fff' if a>0.55 else '#1a1a1a'};font-weight:500"
        return "background-color:rgba(128,128,128,0.15);color:#1a1a1a"

    return df.style.format(fmt).applymap(_s)


def _esc_column_config(cols, pct=False):
    fmt = "%.1f%%" if pct else "%.1f"
    return {c: st.column_config.NumberColumn(c, format=fmt) for c in cols}


# T_max y costo FV para %PnL
_expiry_dates_sc = []
for _lg in legs:
    try:
        _expiry_dates_sc.append(pd.to_datetime(str(_lg["expiry"])[:10]).date())
    except Exception:
        pass
_expiry_date = max(_expiry_dates_sc) if _expiry_dates_sc else today + timedelta(days=365)
_T_max_days = max((_expiry_date - today).days, 0)
_T_max = _T_max_days / 365.0
_r_esc = float(st.session_state.get("ibkr_esc_r", 0.05))
costo_fv = pagado_por_legs * np.exp(_r_esc * _T_max) if pagado_por_legs != 0 else 1.0
df_pct_pnl = (df_pnl / costo_fv * 100).round(1) if costo_fv != 0 else df_pnl * 0

tabla_vista = st.radio(
    "Vista",
    options=["PnL", "Valor", "%PnL"],
    format_func=lambda x: {"PnL": "P&L (valor − pagado)", "Valor": "Valor de la estrategia",
                           "%PnL": "%PnL (P&L / FV pagado)"}[x],
    horizontal=True,
    index=0,
    key="ibkr_esc_tabla_vista",
)
if tabla_vista == "Valor":
    df_show = df_esc
    ref_show = pagado_por_legs
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
st.markdown("**Curvas P&L vs S por fecha**")
colors_sc = plt.cm.tab10(np.linspace(0, 1, n_cols_actual))
fig_sc, ax_sc = plt.subplots(figsize=(11, 4), dpi=100)
S_labels_sc = []
for lbl in df_pnl.index:
    try:
        S_labels_sc.append(float(lbl.split("=")[1].split("_")[0]))
    except Exception:
        S_labels_sc.append(0.0)
for j_col, col_name in enumerate(unique_cols):
    vals  = df_pnl[col_name].values
    disp  = date_cols[j_col] if j_col < len(date_cols) else col_name
    lw    = 2.4 if j_col == 0 else (2.0 if j_col == len(unique_cols) - 1 else 1.3)
    ls    = "-" if j_col in (0, len(unique_cols) - 1) else "--"
    ax_sc.plot(S_labels_sc, vals, color=colors_sc[j_col], linewidth=lw, linestyle=ls, label=disp)
ax_sc.axhline(0, color="black", linewidth=0.8)
S_lo_sc = min(S_desde, S_a); S_hi_sc = max(S_desde, S_a)
if S_lo_sc <= spot <= S_hi_sc:
    ax_sc.axvline(spot, color="#2ca02c", linewidth=1.2, linestyle="--", alpha=0.85, label=f"Spot={spot:.2f}")
for K in sorted(set(all_strikes)):
    ax_sc.axvline(K, color="#ff7f0e", linewidth=0.8, linestyle=":", alpha=0.6, label=f"K={K:.0f}")
ax_sc.set_xlabel("S", fontsize=10); ax_sc.set_ylabel("P&L ($)", fontsize=10)
ax_sc.set_title(f"P&L en distintos momentos — {ticker}", fontsize=11)
handles_sc, labels_sc = ax_sc.get_legend_handles_labels()
seen_sc = {}
for h, lb in zip(handles_sc, labels_sc):
    if lb not in seen_sc:
        seen_sc[lb] = h
ax_sc.legend(seen_sc.values(), seen_sc.keys(), fontsize=8)
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
fn = f"ibkr_escenarios_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
st.download_button("📥 Exportar escenarios a Excel", data=buf.getvalue(), file_name=fn,
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   key="ibkr_export_esc")
