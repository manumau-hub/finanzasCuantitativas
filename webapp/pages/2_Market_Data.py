# -*- coding: utf-8 -*-
"""Market Data - Precios de activos y opciones NYSE."""
import io
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)
_webapp = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _webapp not in sys.path:
    sys.path.insert(0, _webapp)

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from i18n import _, render_language_selector
from ui_format import fmt_expiries, fmt_expiry, norm_strike

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
    div[class*="block-container"], div[class*="BlockContainer"] { max-width: none !important; }
</style>
""", unsafe_allow_html=True)

render_language_selector()

st.title(_("md.title"))

with st.expander(f"📖 {_('md.how_to_use')}", expanded=False):
    st.markdown(f"""
    1. {_("md.help_1")}
    2. {_("md.help_2")}
    3. {_("md.help_3")}
    4. {_("md.help_4")}
    5. {_("md.help_5")}
    6. {_("md.help_6")}
    """)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _fetch_company_info(ticker: str) -> dict:
    """Intenta obtener info extendida vía yfinance. Devuelve dict, nunca lanza excepción."""
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info or {}
        return {
            "sector":      info.get("sector") or info.get("category"),
            "industry":    info.get("industry"),
            "market_cap":  info.get("marketCap"),
            "volume":      info.get("regularMarketVolume") or info.get("volume"),
            "avg_volume":  info.get("averageVolume"),
            "high_52w":    info.get("fiftyTwoWeekHigh"),
            "low_52w":     info.get("fiftyTwoWeekLow"),
            "pe":          info.get("trailingPE"),
            "description": info.get("longBusinessSummary"),
        }
    except Exception:
        return {}


def _fetch_history(ticker: str) -> "pd.DataFrame | None":
    """Histórico de 1 año de precios de cierre. Devuelve DataFrame o None."""
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="1y", auto_adjust=True)
        if not hist.empty:
            return hist[["Close"]].rename(columns={"Close": "Precio"})
    except Exception:
        pass
    return None


def _fmt_large(n) -> str:
    if n is None:
        return "—"
    try:
        n = float(n)
        if n >= 1e12:
            return f"${n/1e12:.2f}T"
        if n >= 1e9:
            return f"${n/1e9:.2f}B"
        if n >= 1e6:
            return f"${n/1e6:.1f}M"
        return f"{n:,.0f}"
    except Exception:
        return "—"


def _fetch_r_subprocess() -> float:
    try:
        _script = os.path.join(os.path.dirname(__file__), "..", "_fetch_r.py")
        out = subprocess.run(
            [sys.executable, _script], capture_output=True, text=True, timeout=20, cwd=_root,
        )
        if out.returncode == 0 and out.stdout.strip():
            return float(out.stdout.strip().split("|")[0])
    except Exception:
        pass
    return 0.05


# ════════════════════════════════════════════════════════════════════════════
# INPUT
# ════════════════════════════════════════════════════════════════════════════
col_ticker, col_btn = st.columns([4, 1])
with col_ticker:
    ticker = st.text_input(_("md.ticker"), value="AAPL").strip().upper()
with col_btn:
    st.write(""); st.write("")
    cargar = st.button(_("md.load"), type="primary")

if not ticker:
    st.stop()

if cargar:
    for k in ["md_spot", "md_quote", "md_exps", "md_error", "md_error_tb",
              "md_info", "md_history", "md_chain"]:
        st.session_state.pop(k, None)
    st.session_state["md_ticker"] = ticker

    try:
        from Codigo.data.market_data import get_spot, get_quote, get_expirations
    except Exception as e:
        st.session_state["md_error"] = str(e)
        if "numpy.dtype" in str(e) or "binary incompatibility" in str(e):
            st.session_state["md_error"] += "\n\n" + _("md.error_numpy")
        st.rerun()

    _orig_stderr = sys.stderr
    try:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        pass
    try:
        with st.spinner(_("md.loading_data", ticker=ticker)):
            try:
                st.session_state["md_spot"]   = get_spot(ticker)
                st.session_state["md_source"] = get_spot.last_source or "—"
            except Exception as e:
                st.session_state["md_error"]    = str(e)
                st.session_state["md_error_tb"] = traceback.format_exc()
            try:
                st.session_state["md_quote"] = get_quote(ticker)
            except Exception:
                st.session_state["md_quote"] = {}
            try:
                st.session_state["md_exps"] = fmt_expiries(get_expirations(ticker))
            except Exception:
                st.session_state["md_exps"] = []
            st.session_state["md_info"]    = _fetch_company_info(ticker)
            st.session_state["md_history"] = _fetch_history(ticker)
    finally:
        try:
            if sys.stderr != _orig_stderr:
                sys.stderr.close()
            sys.stderr = _orig_stderr
        except Exception:
            pass

# ── Guard ─────────────────────────────────────────────────────────────────────
if "md_error" in st.session_state:
    loaded = st.session_state.get("md_ticker", ticker)
    st.error(_("md.error_price", loaded=loaded))
    st.code(st.session_state["md_error"], language=None)
    with st.expander(_("md.traceback")):
        st.code(st.session_state.get("md_error_tb", ""), language="python")
    st.stop()

if "md_spot" not in st.session_state:
    st.info(_("md.enter_ticker"))
    st.stop()

spot          = st.session_state["md_spot"]
quote         = st.session_state.get("md_quote", {})
exps          = fmt_expiries(st.session_state.get("md_exps", []))
info          = st.session_state.get("md_info", {})
history_df    = st.session_state.get("md_history")
loaded_ticker = st.session_state.get("md_ticker", ticker)
name          = quote.get("name") or loaded_ticker

# ════════════════════════════════════════════════════════════════════════════
# PANEL DE COTIZACIÓN
# ════════════════════════════════════════════════════════════════════════════
st.subheader(f"{name}  ({loaded_ticker})")
if info.get("sector"):
    st.caption(f"{info.get('sector', '')}  ·  {info.get('industry', '')}")

# Métricas principales
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric(_("md.price"), f"${spot:.2f}")
with m2:
    chg = quote.get("change"); pct = quote.get("changePercent")
    if chg is not None and pct is not None:
        st.metric(_("md.change_1d"), f"{chg:+.2f}", delta=f"{pct:+.2f}%")
    else:
        st.metric(_("md.change_1d"), "—")
with m3:
    lo = info.get("low_52w"); hi = info.get("high_52w")
    if lo and hi:
        st.metric(_("md.range_52w"), f"${lo:.2f} – ${hi:.2f}")
    else:
        st.metric(_("md.range_52w"), "—")
with m4:
    st.metric(_("md.market_cap"), _fmt_large(info.get("market_cap")))
with m5:
    st.metric(_("md.volume"), _fmt_large(info.get("volume")))

# Extra: P/E y volumen promedio
ex1, ex2, ex3 = st.columns(3)
with ex1:
    pe = info.get("pe")
    st.caption(f"{_('md.pe')} {pe:.1f}" if pe else f"{_('md.pe')} —")
with ex2:
    st.caption(f"{_('md.avg_volume')} {_fmt_large(info.get('avg_volume'))}")
with ex3:
    st.caption(f"{_('md.spot_source')} {st.session_state.get('md_source', '—')}")

# Gráfico histórico
if history_df is not None and not history_df.empty:
    with st.expander(_("md.historical_chart"), expanded=False):
        fig_h, ax_h = plt.subplots(figsize=(11, 2.8), dpi=100)
        ax_h.plot(history_df.index, history_df["Precio"], color="#1f77b4", linewidth=1.4)
        ax_h.axhline(spot, color="#d62728", linewidth=0.9, linestyle="--", alpha=0.7)
        ax_h.fill_between(history_df.index, history_df["Precio"],
                          history_df["Precio"].min(), alpha=0.07, color="#1f77b4")
        ax_h.set_ylabel(_("md.price_usd"), fontsize=9)
        ax_h.set_title(_("md.chart_title", ticker=loaded_ticker), fontsize=10)
        ax_h.grid(True, alpha=0.2)
        ax_h.tick_params(labelsize=8)
        plt.tight_layout()
        st.pyplot(fig_h, use_container_width=True)
        plt.close(fig_h)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# OPTIONS CHAIN
# ════════════════════════════════════════════════════════════════════════════
if not exps:
    st.warning(_("md.no_options", ticker=loaded_ticker))
    st.stop()

col_exp, col_btn2 = st.columns([3, 1])
with col_exp:
    expiration = st.selectbox(
        _("md.expiration"),
        options=exps,
        index=0,
        format_func=lambda e: fmt_expiry(e),
    )
with col_btn2:
    st.write(""); st.write("")
    cargar_opts = st.button(_("md.load_options"), type="primary", use_container_width=True)

expiration = fmt_expiry(expiration)

if cargar_opts:
    from Codigo.data.market_data import get_options_chain
    with st.spinner(_("md.loading_chain")):
        try:
            st.session_state["md_chain"] = get_options_chain(loaded_ticker, expiration)
            st.session_state["md_exp_loaded"] = expiration
        except Exception as e:
            st.error(_("md.error_chain"))
            st.code(str(e))

if "md_chain" not in st.session_state:
    st.info(_("md.select_exp"))
    st.stop()

chain_df    = st.session_state["md_chain"]
exp_loaded  = fmt_expiry(st.session_state.get("md_exp_loaded", expiration))

import pandas as pd  # Lazy: solo cuando hay chain (evita error numpy/pandas al cargar página)

# ── Filtros ───────────────────────────────────────────────────────────────────
st.markdown(_("md.filters"))
ff1, ff2, ff3 = st.columns(3)
with ff1:
    strike_min = st.number_input(
        _("md.strike_min"),
        value=norm_strike(spot * 0.8),
        step=1.0,
        format="%.2f",
        key="smin",
    )
with ff2:
    strike_max = st.number_input(
        _("md.strike_max"),
        value=norm_strike(spot * 1.2),
        step=1.0,
        format="%.2f",
        key="smax",
    )
with ff3:
    _FILT_VALS = ["Ambas", "Solo Calls", "Solo Puts"]
    tipo_filter = st.radio(
        _("md.show"), _FILT_VALS, horizontal=True, key="md_tipo_filter",
        format_func=lambda x: _("md.show_both") if x == "Ambas" else (_("md.show_calls") if x == "Solo Calls" else _("md.show_puts"))
    )

filtered = chain_df[
    (chain_df["strike"] >= strike_min) & (chain_df["strike"] <= strike_max)
].copy()

# ── Calcular Mid y Spread antes de pivotar ────────────────────────────────────
def _add_mid_spread(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "bid" in df.columns and "ask" in df.columns:
        bid = pd.to_numeric(df["bid"], errors="coerce")
        ask = pd.to_numeric(df["ask"], errors="coerce")
        df["mid"]    = ((bid + ask) / 2).round(3)
        df["spread"] = (ask - bid).round(3)
    return df

filtered = _add_mid_spread(filtered)

# ── Pivot ─────────────────────────────────────────────────────────────────────
pivot_cols = ["strike", "bid", "ask", "mid", "spread", "lastPrice",
              "impliedVolatility", "volume", "openInterest"]
avail = [c for c in pivot_cols if c in filtered.columns]

calls_raw = filtered[filtered["type"] == "call"][avail].copy()
puts_raw  = filtered[filtered["type"] == "put"][avail].copy()

call_rename = {c: f"C_{c}" if c != "strike" else "Strike" for c in avail}
put_rename  = {c: f"P_{c}" if c != "strike" else "Strike" for c in avail}
calls_piv = calls_raw.rename(columns=call_rename)
puts_piv  = puts_raw.rename(columns=put_rename)

if tipo_filter == "Solo Calls":
    merged = calls_piv.sort_values("Strike")
elif tipo_filter == "Solo Puts":
    merged = puts_piv.sort_values("Strike")
else:
    merged = pd.merge(calls_piv, puts_piv, on="Strike", how="outer").sort_values("Strike")

if "Strike" in merged.columns:
    merged["Strike"] = merged["Strike"].map(norm_strike)

# ── Resumen de chain ──────────────────────────────────────────────────────────
from Codigo.data.market_data import get_implied_vol_atm_with_source

iv_atm_res = get_implied_vol_atm_with_source(chain_df, spot, exp_loaded)
iv_atm     = iv_atm_res[0] if iv_atm_res else None

oi_calls = pd.to_numeric(calls_raw.get("openInterest", pd.Series(dtype=float)), errors="coerce").sum()
oi_puts  = pc_ratio = None
if "openInterest" in puts_raw.columns:
    oi_puts = pd.to_numeric(puts_raw["openInterest"], errors="coerce").sum()
vol_calls = pd.to_numeric(calls_raw.get("volume", pd.Series(dtype=float)), errors="coerce").sum()
vol_puts  = pd.to_numeric(puts_raw.get("volume", pd.Series(dtype=float)), errors="coerce").sum() if "volume" in puts_raw.columns else None

pc_ratio = (oi_puts / oi_calls) if (oi_calls and oi_puts and oi_calls > 0) else None

# Strike con mayor OI (calls + puts)
max_oi_strike = None
try:
    oi_all = filtered.groupby("strike")["openInterest"].sum()
    max_oi_strike = float(oi_all.idxmax()) if not oi_all.empty else None
except Exception:
    pass

st.markdown(_("md.chain_summary"))
rs1, rs2, rs3, rs4, rs5 = st.columns(5)
with rs1:
    st.metric(_("md.iv_atm"), f"{iv_atm*100:.1f}%" if iv_atm else "—")
with rs2:
    st.metric(_("md.pc_ratio"), f"{pc_ratio:.2f}" if pc_ratio else "—")
with rs3:
    st.metric(_("md.oi_total"), f"{int(oi_calls + (oi_puts or 0)):,}" if oi_calls else "—")
with rs4:
    vol_total = (vol_calls or 0) + (vol_puts or 0)
    st.metric(_("md.vol_total"), f"{int(vol_total):,}" if vol_total else "—")
with rs5:
    st.metric(_("md.max_oi_strike"), f"${max_oi_strike:.0f}" if max_oi_strike else "—")

# ── IV Smile ──────────────────────────────────────────────────────────────────
with st.expander(_("md.iv_smile"), expanded=True):
    try:
        smile_calls = calls_raw[["strike", "impliedVolatility"]].dropna().copy() if "impliedVolatility" in calls_raw.columns else pd.DataFrame()
        smile_puts  = puts_raw[["strike", "impliedVolatility"]].dropna().copy()  if "impliedVolatility" in puts_raw.columns  else pd.DataFrame()

        # Filtrar IVs inválidas (0 o >300%)
        if not smile_calls.empty:
            smile_calls = smile_calls[(smile_calls["impliedVolatility"] > 0.001) & (smile_calls["impliedVolatility"] < 3.0)]
        if not smile_puts.empty:
            smile_puts = smile_puts[(smile_puts["impliedVolatility"] > 0.001) & (smile_puts["impliedVolatility"] < 3.0)]

        if not smile_calls.empty or not smile_puts.empty:
            fig_smile, ax_s = plt.subplots(figsize=(11, 3.5), dpi=100)
            if not smile_calls.empty:
                ax_s.plot(smile_calls["strike"], smile_calls["impliedVolatility"] * 100,
                          "o-", color="#2ca02c", linewidth=1.6, markersize=4, label="IV Call")
            if not smile_puts.empty:
                ax_s.plot(smile_puts["strike"], smile_puts["impliedVolatility"] * 100,
                          "s-", color="#d62728", linewidth=1.6, markersize=4, label="IV Put")
            ax_s.axvline(spot, color="#1f77b4", linewidth=1.3, linestyle="--", alpha=0.8, label=f"Spot = {spot:.2f}")
            ax_s.set_xlabel("Strike", fontsize=10)
            ax_s.set_ylabel("IV (%)", fontsize=10)
            ax_s.set_title(_("md.iv_smile_title", ticker=loaded_ticker, exp=exp_loaded), fontsize=11)
            ax_s.legend(fontsize=9)
            ax_s.grid(True, alpha=0.2)
            plt.tight_layout()
            st.pyplot(fig_smile, use_container_width=True)
            plt.close(fig_smile)
        else:
            st.caption(_("md.no_iv_data"))
    except Exception as e:
        st.caption(_("md.smile_error", e=str(e)))

# ── Griegas ───────────────────────────────────────────────────────────────────
mostrar_griegas = st.checkbox(_("md.show_greeks"), value=False, key="md_mostrar_griegas")
if mostrar_griegas:
    try:
        from Codigo.pricing.american_greeks_ql import gregas_americana_baw_ql
        from Codigo.data.market_data import get_dividend_yield

        r_rate = _fetch_r_subprocess()
        div    = get_dividend_yield(loaded_ticker)
        try:
            exp_dt = datetime.strptime(str(exp_loaded)[:10], "%Y-%m-%d").date()
        except Exception:
            exp_dt = datetime.now().date()
        T = max((exp_dt - datetime.now().date()).days / 365.0, 1 / 365)

        delta_c, gamma_c, vega_c, theta_c = [], [], [], []
        delta_p, gamma_p, vega_p, theta_p = [], [], [], []
        with st.spinner(_("md.calc_greeks")):
            for _unused, row in merged.iterrows():
                K    = float(row["Strike"])
                iv_c = row.get("C_impliedVolatility")
                iv_p = row.get("P_impliedVolatility")
                sc   = float(iv_c) if pd.notna(iv_c) and float(iv_c if iv_c is not None else 0) > 0 else 0.25
                sp   = float(iv_p) if pd.notna(iv_p) and float(iv_p if iv_p is not None else 0) > 0 else 0.25
                for tp, sig, dl, gl, vl, tl in [("C", sc, delta_c, gamma_c, vega_c, theta_c),
                                                  ("P", sp, delta_p, gamma_p, vega_p, theta_p)]:
                    try:
                        g = gregas_americana_baw_ql(tp, spot, K, T, r_rate, sig, div)
                        dl.append(round(g["delta"], 4)); gl.append(round(g["gamma"], 4))
                        vl.append(round(g["vega"],  2)); tl.append(round(g["theta"], 2))
                    except Exception:
                        dl.append(None); gl.append(None); vl.append(None); tl.append(None)

        if tipo_filter != "Solo Puts":
            merged["Δ CALL"] = delta_c; merged["Γ CALL"] = gamma_c
            merged["ν CALL"] = vega_c;  merged["Θ CALL"] = theta_c
        if tipo_filter != "Solo Calls":
            merged["Δ PUT"]  = delta_p; merged["Γ PUT"]  = gamma_p
            merged["ν PUT"]  = vega_p;  merged["Θ PUT"]  = theta_p
    except ImportError:
        st.warning(_("md.quantlib_required"))

# ── Opciones de visualización ─────────────────────────────────────────────────
ocultar_precios    = st.checkbox(_("md.hide_prices"), value=False, key="md_ocultar_precios")
ocultar_iv_vol_oi  = st.checkbox(_("md.hide_iv_vol_oi"), value=False, key="md_ocultar_iv_vol_oi")

# ── Formateo de columnas ──────────────────────────────────────────────────────
display_cols = {
    "C_bid": "BID C", "C_ask": "ASK C", "C_mid": "MID C", "C_spread": "SPR C",
    "C_lastPrice": "LAST C", "C_impliedVolatility": "IV C %",
    "C_volume": "Vol C", "C_openInterest": "OI C",
    "P_bid": "BID P", "P_ask": "ASK P", "P_mid": "MID P", "P_spread": "SPR P",
    "P_lastPrice": "LAST P", "P_impliedVolatility": "IV P %",
    "P_volume": "Vol P", "P_openInterest": "OI P",
}
merged = merged.rename(columns=display_cols)

for c in merged.columns:
    if c == "Strike":
        continue
    if "IV" in c:
        merged[c] = (pd.to_numeric(merged[c], errors="coerce").fillna(0) * 100).round(1)
    elif merged[c].dtype in ("float64", "float32"):
        merged[c] = merged[c].round(3)

# Orden de columnas
call_price_cols  = ["BID C", "ASK C", "MID C", "SPR C", "LAST C"]
call_info_cols   = ["IV C %", "Vol C", "OI C"]
call_greek_cols  = ["Δ CALL", "Γ CALL", "ν CALL", "Θ CALL"]
put_price_cols   = ["BID P", "ASK P", "MID P", "SPR P", "LAST P"]
put_info_cols    = ["IV P %", "Vol P", "OI P"]
put_greek_cols   = ["Δ PUT", "Γ PUT", "ν PUT", "Θ PUT"]

left_cols  = [c for c in (call_price_cols if not ocultar_precios else []) +
              (call_info_cols if not ocultar_iv_vol_oi else []) +
              (call_greek_cols if mostrar_griegas else []) if c in merged.columns]
right_cols = [c for c in (put_price_cols if not ocultar_precios else []) +
              (put_info_cols if not ocultar_iv_vol_oi else []) +
              (put_greek_cols if mostrar_griegas else []) if c in merged.columns]
col_order  = left_cols + (["Strike"] if "Strike" in merged.columns else []) + right_cols
merged     = merged[[c for c in col_order if c in merged.columns]]

# ── Tabla HTML ────────────────────────────────────────────────────────────────
merged_reset = merged.reset_index(drop=True)
strike_idx   = list(merged_reset.columns).index("Strike") + 1 if "Strike" in merged_reset.columns else 0
atm_row_idx  = int((merged_reset["Strike"] - spot).abs().idxmin()) if "Strike" in merged_reset.columns and len(merged_reset) > 0 else -1

html = merged_reset.to_html(index=False, classes="options-chain-table", border=0, na_rep="—")

# Colorear headers
for col in merged_reset.columns:
    if col in ("BID C","ASK C","MID C","SPR C","LAST C","IV C %","Vol C","OI C","Δ CALL","Γ CALL","ν CALL","Θ CALL"):
        html = html.replace(f"<th>{col}</th>", f'<th style="background:#d4edda">{col}</th>')
    elif col in ("BID P","ASK P","MID P","SPR P","LAST P","IV P %","Vol P","OI P","Δ PUT","Γ PUT","ν PUT","Θ PUT"):
        html = html.replace(f"<th>{col}</th>", f'<th style="background:#f8d7da">{col}</th>')
    elif col == "Strike":
        html = html.replace(f"<th>{col}</th>", f'<th style="background:#cce5ff">{col}</th>')

# Resaltar fila ATM completa
if atm_row_idx >= 0:
    tbody_match = re.search(r"<tbody>(.*?)</tbody>", html, re.DOTALL)
    if tbody_match:
        tbody_inner = tbody_match.group(1)
        row_count   = [0]

        def _atm_class(m):
            cls = ' class="atm-row"' if row_count[0] == atm_row_idx else ""
            row_count[0] += 1
            return f"<tr{cls}>{m.group(1)}</tr>"

        new_tbody = re.sub(r"<tr>(.*?)</tr>", _atm_class, tbody_inner, flags=re.DOTALL)
        html = html.replace(tbody_inner, new_tbody)

css_strike_col  = f".options-chain-table tbody tr td:nth-child({strike_idx}) {{ background:#cce5ff; }}\n" if strike_idx > 0 else ""
css_atm_strike  = f".options-chain-table tbody tr.atm-row td:nth-child({strike_idx}) {{ background:#2176ae !important; color:#fff !important; font-weight:700; }}\n" if strike_idx > 0 else ""

css = f"""
<style>
.options-chain-wrapper {{ overflow-x: auto; max-width: 100%; margin: 0.5rem 0; }}
.options-chain-table {{ width: max-content; border-collapse: collapse; font-size: 0.88rem; }}
.options-chain-table th, .options-chain-table td {{ padding: 0.3rem 0.55rem; text-align: right; border: 1px solid #ddd; white-space: nowrap; }}
.options-chain-table th {{ font-weight: 600; }}
.options-chain-table tbody tr.atm-row td {{ background: #fff8e1 !important; font-weight: 600; }}
{css_strike_col}{css_atm_strike}
</style>"""

st.markdown(css + '<div class="options-chain-wrapper">' + html + "</div>", unsafe_allow_html=True)
st.caption(_("md.atm_caption", spot=f"{spot:.2f}"))

# ── Exportar ──────────────────────────────────────────────────────────────────
buf = io.BytesIO()
merged_reset.to_excel(buf, index=False, sheet_name="Options Chain", engine="openpyxl")
buf.seek(0)
fn = f"options_chain_{loaded_ticker}_{str(exp_loaded)[:10]}.xlsx"
st.download_button(_("md.export_excel"), data=buf, file_name=fn,
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   key="md_export_chain")

st.caption(_("md.footer_strategies"))
