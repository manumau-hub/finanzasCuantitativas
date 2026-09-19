# -*- coding: utf-8 -*-
"""
Griegas — Delta, Gamma, Vega, Rho, Theta vs Spot.

Fórmulas analíticas de Black-Scholes para opciones europeas.
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from i18n import _, render_language_selector
from Codigo.analytics.gregas_bs import delta_bs, gamma_bs, vega_bs, rho_bs, theta_bs
from Codigo.pricing import ESTRATEGIA_PIERNAS
from Codigo.pricing.european_bs import opcion_europea_bs

try:
    from Codigo.analytics.gregas_bs import (
        theta_per_day_bs, dividend_rho_bs, strike_sensitivity_bs, elasticity_bs,
    )
except ImportError:
    def theta_per_day_bs(tipo, S, K, T, r, sigma, div):
        return theta_bs(tipo, S, K, T, r, sigma, div) / 365.0

    def dividend_rho_bs(tipo, S, K, T, r, sigma, div):
        from Codigo.analytics.gregas_bs import _d1_d2
        import math
        from scipy.stats import norm
        d1, _ = _d1_d2(S, K, T, r, sigma, div)
        factor = T * S * math.exp(-div * T)
        return -factor * norm.cdf(d1) if tipo == "C" else factor * norm.cdf(-d1)

    def strike_sensitivity_bs(tipo, S, K, T, r, sigma, div):
        from Codigo.analytics.gregas_bs import _d1_d2
        import math
        from scipy.stats import norm
        _, d2 = _d1_d2(S, K, T, r, sigma, div)
        f = math.exp(-r * T)
        return -f * norm.cdf(d2) if tipo == "C" else f * norm.cdf(-d2)

    def elasticity_bs(tipo, S, K, T, r, sigma, div):
        V = opcion_europea_bs(tipo, S, K, T, r, sigma, div)
        return float("nan") if V <= 0 else S * delta_bs(tipo, S, K, T, r, sigma, div) / V

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
    div[class*="block-container"], div[class*="BlockContainer"] { max-width: none !important; }
</style>
""", unsafe_allow_html=True)

render_language_selector()

st.title(_("griegas.title"))

with st.expander(f"📖 {_('griegas.how_to_use')}", expanded=False):
    st.markdown(f"""
    1. {_("griegas.help_1")}
    2. {_("griegas.help_2")}
    3. {_("griegas.help_3")}
    4. {_("griegas.help_4")}
    5. {_("griegas.help_5")}
    """)

# ── Session state ─────────────────────────────────────────────────────────────
if "griegas_legs" not in st.session_state:
    st.session_state["griegas_legs"] = []

# ── Definiciones ──────────────────────────────────────────────────────────────
_GREEK_FUNCS = {
    "Delta":             delta_bs,
    "Gamma":             gamma_bs,
    "Vega":              vega_bs,
    "Rho":               rho_bs,
    "Theta":             theta_bs,
    "Theta (por día)":   theta_per_day_bs,
    "DividendRho":       dividend_rho_bs,
    "StrikeSensitivity": strike_sensitivity_bs,
    "Elasticity":        elasticity_bs,
}
_ALL_GREEKS  = list(_GREEK_FUNCS.keys())
_GREEK_DEFS  = {
    "Delta":             "**Δ = ∂V/∂S** — Sensibilidad ante cambio en spot. Call ∈ [0,1], Put ∈ [-1,0]. ATM ≈ ±0.5.",
    "Gamma":             "**Γ = ∂²V/∂S²** — Curvatura del precio. Máxima ATM. Mide velocidad de cambio del Delta.",
    "Vega":              "**ν = ∂V/∂σ** — Sensibilidad ante cambio en vol implícita (+1%). Siempre positiva en vanilla.",
    "Rho":               "**ρ = ∂V/∂r** — Sensibilidad ante cambio en tasa libre de riesgo. Call>0, Put<0.",
    "Theta":             "**Θ = ∂V/∂T** — Decay temporal (por año). Típicamente negativo: el tiempo destruye valor.",
    "Theta (por día)":   "**Θ/365** — Decay diario. Más intuitivo para gestión operativa.",
    "DividendRho":       "**∂V/∂q** — Sensibilidad ante cambio en dividendos. Call<0 (más div → menos valor call).",
    "StrikeSensitivity": "**∂V/∂K** — Sensibilidad ante cambio en el strike. Call<0, Put>0.",
    "Elasticity":        "**ε = S·Δ/V** — Elasticidad: cambio % en V ante 1% de cambio en S. Alto en OTM (apalancamiento).",
}
_TAB10 = plt.cm.tab10.colors  # type: ignore[attr-defined]

# ════════════════════════════════════════════════════════════════════════════
# PARÁMETROS GLOBALES
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("griegas.params_global"))
cg1, cg2, cg3 = st.columns(3)
with cg1: r   = st.number_input(_("prop.r_rate"),       value=0.05, min_value=0.0, max_value=1.0, format="%.3f", key="g_r")
with cg2: div = st.number_input(_("prop.div_dividends"), value=0.0, min_value=0.0, max_value=1.0, format="%.3f", key="g_div")
with cg3: S_actual = st.number_input(_("griegas.s_actual"), value=100.0, min_value=0.1, step=1.0, key="g_s_actual")

# ════════════════════════════════════════════════════════════════════════════
# MODO
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("griegas.mode"))
modo = st.radio(_("griegas.mode"), options=["Opción única", "Portfolio"],
                format_func=lambda x: _("griegas.mode_single") if x == "Opción única" else _("griegas.mode_portfolio"),
                horizontal=True, key="griegas_modo")

if modo == "Opción única":
    c1, c2, c3, c4 = st.columns(4)
    with c1: K     = st.number_input(_("prop.k_strike"),   value=100.0, min_value=0.1, step=1.0,  key="g_K")
    with c2: T     = st.number_input(_("prop.t_years"),     value=1.0,   min_value=0.01, step=0.1, key="g_T")
    with c3: sigma = st.number_input(_("prop.sigma_vol"),  value=0.25,  min_value=0.01, max_value=2.0, format="%.3f", key="g_sigma")
    with c4: tipo  = st.radio(_("me.type"), ["C", "P"], horizontal=True, key="g_tipo")

else:
    # ── Portfolio ──────────────────────────────────────────────────────────
    legs = st.session_state["griegas_legs"]
    K_ref = legs[0]["K"] if legs else 100.0

    st.markdown(f"**{_('griegas.typical_strategy')}**")
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
    _CHOOSE_KEY = ""
    opts = [_CHOOSE_KEY] + list(_ESTR_NOMBRES.keys())
    estrategia_sel = st.selectbox(
        _("griegas.strategy"), opts, index=0,
        format_func=lambda x: _("griegas.choose_strategy") if x == _CHOOSE_KEY else _ESTR_NOMBRES[x], key="g_estr_sel",
    )

    p1, p2 = st.columns(2)
    with p1: T_port     = st.number_input(_("griegas.t_all_legs"), value=1.0, min_value=0.01, step=0.1, key="g_T_port")
    with p2: sigma_port = st.number_input(_("griegas.iv_all_legs"), value=0.25, min_value=0.01, max_value=2.0, format="%.3f", key="g_sigma_port")

    if estrategia_sel != _CHOOSE_KEY:
        if estrategia_sel in ("straddle", "short_straddle", "covered_call", "protective_put"):
            K1 = st.number_input("K", value=K_ref, min_value=0.1, key="g_estr_K")
            estr_kwargs = {"K": K1}
        elif estrategia_sel in ("strangle", "short_strangle", "combo", "collar", "box",
                                "bull_call_spread", "bear_call_spread", "bull_put_spread", "bear_put_spread"):
            ec1, ec2 = st.columns(2)
            with ec1: K1 = st.number_input("K1", value=round(K_ref * 0.9, 2), min_value=0.1, key="g_estr_K1")
            with ec2: K2 = st.number_input("K2", value=round(K_ref * 1.1, 2), min_value=0.1, key="g_estr_K2")
            estr_kwargs = {"K1": K1, "K2": K2}
        elif estrategia_sel == "ratio_spread":
            ec1, ec2, ec3, ec4 = st.columns(4)
            with ec1: K1 = st.number_input("K1", value=round(K_ref * 0.95, 2), min_value=0.1, key="g_estr_K1")
            with ec2: K2 = st.number_input("K2", value=round(K_ref * 1.05, 2), min_value=0.1, key="g_estr_K2")
            with ec3: n1 = st.number_input("n1", value=1, min_value=1, key="g_estr_n1")
            with ec4: n2 = st.number_input("n2", value=2, min_value=1, key="g_estr_n2")
            estr_kwargs = {"K1": K1, "K2": K2, "n1": int(n1), "n2": int(n2)}
        elif estrategia_sel in ("call_butterfly", "put_butterfly", "iron_butterfly"):
            ec1, ec2, ec3 = st.columns(3)
            with ec1: K1 = st.number_input("K1", value=round(K_ref * 0.9, 2), min_value=0.1, key="g_estr_K1")
            with ec2: K2 = st.number_input("K2", value=K_ref, min_value=0.1, key="g_estr_K2")
            with ec3: K3 = st.number_input("K3", value=round(K_ref * 1.1, 2), min_value=0.1, key="g_estr_K3")
            estr_kwargs = {"K1": K1, "K2": K2, "K3": K3}
        else:
            ec1, ec2, ec3, ec4 = st.columns(4)
            with ec1: K1 = st.number_input("K1", value=round(K_ref * 0.85, 2), min_value=0.1, key="g_estr_K1")
            with ec2: K2 = st.number_input("K2", value=round(K_ref * 0.95, 2), min_value=0.1, key="g_estr_K2")
            with ec3: K3 = st.number_input("K3", value=round(K_ref * 1.05, 2), min_value=0.1, key="g_estr_K3")
            with ec4: K4 = st.number_input("K4", value=round(K_ref * 1.15, 2), min_value=0.1, key="g_estr_K4")
            estr_kwargs = {"K1": K1, "K2": K2, "K3": K3, "K4": K4}

        if st.button(_("griegas.load_strategy"), key="g_cargar_estr"):
            piernas = ESTRATEGIA_PIERNAS[estrategia_sel](**estr_kwargs)
            st.session_state["griegas_legs"] = [
                {"K": float(k), "T": T_port, "tipo": t, "qty": int(c), "sigma": sigma_port}
                for t, k, c in piernas
            ]
            st.rerun()

    st.markdown(f"**{_('griegas.legs_portfolio')}**")
    for i, leg in enumerate(legs):
        lc1, lc2, lc3, lc4, lc5, lc6 = st.columns([1, 1, 0.8, 1, 1, 0.3])
        with lc1: legs[i]["K"]     = st.number_input("K",       value=float(leg["K"]),     min_value=0.1, step=1.0,  key=f"leg_K_{i}")
        with lc2: legs[i]["T"]     = st.number_input(_("prop.t_years"), value=float(leg["T"]),     min_value=0.01, step=0.1, key=f"leg_T_{i}")
        with lc3: legs[i]["tipo"]  = st.selectbox(_("me.type"), ["C", "P"], index=0 if leg["tipo"] == "C" else 1, key=f"leg_tipo_{i}")
        with lc4: legs[i]["qty"]   = st.number_input(_("griegas.cant"),     value=int(leg["qty"]),     step=1,        key=f"leg_qty_{i}")
        with lc5: legs[i]["sigma"] = st.number_input("IV",       value=float(leg["sigma"]), min_value=0.01, max_value=2.0, format="%.3f", key=f"leg_sigma_{i}")
        with lc6:
            if st.button("🗑", key=f"leg_del_{i}"):
                legs.pop(i); st.rerun()

    if st.button(_("griegas.add_leg"), key="g_leg_add"):
        legs.append({"K": K_ref, "T": T_port if "T_port" in dir() else 1.0,
                     "tipo": "C", "qty": 1,
                     "sigma": sigma_port if "sigma_port" in dir() else 0.25})
        st.rerun()

    if not legs:
        st.warning(_("griegas.load_or_add"))

# ════════════════════════════════════════════════════════════════════════════
# GRIEGA + OPCIONES DE GRÁFICO
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("griegas.greek"))

_GREEK_DEF_KEYS = {
    "Delta": "griegas.def_delta", "Gamma": "griegas.def_gamma", "Vega": "griegas.def_vega",
    "Rho": "griegas.def_rho", "Theta": "griegas.def_theta", "Theta (por día)": "griegas.def_theta_day",
    "DividendRho": "griegas.def_dividend_rho", "StrikeSensitivity": "griegas.def_strike_sens",
    "Elasticity": "griegas.def_elasticity",
}
col_g, col_opts = st.columns([2, 3])
with col_g:
    griega_sel = st.selectbox(_("griegas.greek_to_plot"), _ALL_GREEKS, key="g_griega_sel")

with st.expander(_("griegas.what_is", name=griega_sel), expanded=False):
    _def_key = _GREEK_DEF_KEYS.get(griega_sel)
    st.markdown(_(_def_key) if _def_key else "—")

ambos_tipos   = False
T_extra_list  = []
leg_breakdown = False

if modo == "Opción única":
    with col_opts:
        ambos_tipos  = st.checkbox(_("griegas.overlay_call_put"), value=False, key="g_ambos_tipos")
        T_opciones   = [0.08, 0.17, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
        T_extra_list = st.multiselect(
            _("griegas.compare_t"),
            options=T_opciones,
            default=[],
            format_func=lambda x: f"T={x}",
            key="g_T_extra",
        )
elif modo == "Portfolio":
    with col_opts:
        leg_breakdown = st.checkbox(_("griegas.leg_breakdown"), value=False, key="g_leg_breakdown")

# ── Rango S ───────────────────────────────────────────────────────────────────
_legs_ss = st.session_state.get("griegas_legs", [])
_K_ref   = (_legs_ss[0]["K"] if modo == "Portfolio" and _legs_ss else
            (K if modo == "Opción única" else 100.0))

col_smin, col_smax = st.columns(2)
with col_smin: S_min = st.number_input(_("griegas.s_from"), value=max(1.0, _K_ref * 0.5), min_value=0.1, step=1.0, key="g_smin")
with col_smax: S_max = st.number_input(_("griegas.s_to"), value=_K_ref * 1.5, min_value=0.1, step=1.0, key="g_smax")

# ════════════════════════════════════════════════════════════════════════════
# CÁLCULO — helpers
# ════════════════════════════════════════════════════════════════════════════
can_compute = (modo == "Opción única") or (modo == "Portfolio" and bool(_legs_ss))
if S_min >= S_max:
    st.error(_("griegas.s_from_to_error"))
    st.stop()
if not can_compute:
    st.info(_("griegas.add_leg_info"))
    st.stop()

S_vals   = np.linspace(S_min, S_max, 200)
greek_fn = _GREEK_FUNCS[griega_sel]


def _single_greek(tipo_leg, S, K_leg, T_leg, sigma_leg):
    if griega_sel == "Elasticity":
        V = opcion_europea_bs(tipo_leg, float(S), K_leg, T_leg, r, sigma_leg, div)
        if V <= 0:
            return np.nan
        return float(S) * delta_bs(tipo_leg, float(S), K_leg, T_leg, r, sigma_leg, div) / V
    return greek_fn(tipo_leg, float(S), K_leg, T_leg, r, sigma_leg, div)


def _portfolio_greek(S, legs_list):
    if griega_sel == "Elasticity":
        V_tot = sum(
            l["qty"] * opcion_europea_bs(l["tipo"], float(S), l["K"], l["T"], r, l["sigma"], div)
            for l in legs_list
        )
        D_tot = sum(
            l["qty"] * delta_bs(l["tipo"], float(S), l["K"], l["T"], r, l["sigma"], div)
            for l in legs_list
        )
        return float(S) * D_tot / V_tot if abs(V_tot) > 1e-10 else np.nan
    return sum(
        l["qty"] * greek_fn(l["tipo"], float(S), l["K"], l["T"], r, l["sigma"], div)
        for l in legs_list
    )


def _compute_curve(tipo_leg, T_leg, legs_list=None):
    out = []
    for S in S_vals:
        try:
            if legs_list is not None:
                out.append(_portfolio_greek(S, legs_list))
            else:
                out.append(_single_greek(tipo_leg, S, K, T_leg, sigma))
        except Exception:
            out.append(np.nan)
    return np.array(out)


# ════════════════════════════════════════════════════════════════════════════
# CONSTRUIR CURVAS
# ════════════════════════════════════════════════════════════════════════════
# Lista de curvas: (label, values, color, linestyle, linewidth, zorder)
curves = []

if modo == "Opción única":
    tipos_a_plot  = (["C", "P"] if ambos_tipos else [tipo])
    _STYLES       = {"C": "-", "P": "--"}
    _TIPO_LABEL   = {"C": "Call", "P": "Put"}
    T_all         = sorted(set([T] + T_extra_list))

    for ci, Ti in enumerate(T_all):
        for tp in tipos_a_plot:
            vals  = _compute_curve(tp, Ti)
            color = _TAB10[ci % len(_TAB10)]
            lw    = 2.2 if Ti == T else 1.4
            if ambos_tipos and len(T_all) > 1:
                label = f"{_TIPO_LABEL[tp]}  T={Ti}"
            elif ambos_tipos:
                label = _TIPO_LABEL[tp]
            elif len(T_all) > 1:
                label = f"T={Ti}"
            else:
                label = f"{griega_sel} ({_TIPO_LABEL[tp]})"
            curves.append((label, vals, color, _STYLES[tp], lw, 3))

else:  # Portfolio
    total_vals = _compute_curve(None, None, legs_list=_legs_ss)
    curves.append((f"{griega_sel} — Portfolio", total_vals, _TAB10[0], "-", 2.4, 4))

    if leg_breakdown:
        for ci, leg in enumerate(_legs_ss):
            lv = _compute_curve(leg["tipo"], leg["T"], legs_list=[leg])
            lw_leg = 1.0
            tp_lbl = "Call" if leg["tipo"] == "C" else "Put"
            label  = f"Leg {ci+1}: {tp_lbl} K={leg['K']:.0f} T={leg['T']} qty={leg['qty']:+d}"
            curves.append((label, lv, _TAB10[(ci + 1) % len(_TAB10)], "--", 1.0, 2))

# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 5), dpi=110)

for label, vals, color, ls, lw, zo in curves:
    valid = np.isfinite(vals)
    if np.any(valid):
        ax.plot(S_vals[valid], vals[valid], color=color, linestyle=ls,
                linewidth=lw, label=label, zorder=zo)

ax.axhline(0, color="gray", linewidth=0.8, linestyle="-")

# Línea K (ATM) — aplica a opción única
if modo == "Opción única" and S_min <= K <= S_max:
    ax.axvline(K, color="#e8750a", linewidth=1.3, linestyle="--", alpha=0.85,
               label=_("griegas.k_atm", k=f"{K:.1f}"))

# En portfolio: marcar todos los strikes de los legs
if modo == "Portfolio":
    _ks_drawn = set()
    for li, leg in enumerate(_legs_ss):
        lk = leg["K"]
        if S_min <= lk <= S_max and lk not in _ks_drawn:
            ax.axvline(lk, color="#e8750a", linewidth=1.0, linestyle="--", alpha=0.6)
            ax.text(lk, ax.get_ylim()[1] if ax.get_ylim()[1] != 0 else 1,
                    f" K={lk:.0f}", color="#e8750a", fontsize=7.5, va="top")
            _ks_drawn.add(lk)

# Línea S actual
if S_min <= S_actual <= S_max:
    ax.axvline(S_actual, color="#2ca02c", linewidth=1.4, linestyle=":",
               label=_("griegas.s_current", s=f"{S_actual:.1f}"), zorder=5)

ax.set_xlabel(_("griegas.spot_s"), fontsize=11)
ax.set_ylabel(griega_sel, fontsize=11)
if modo == "Portfolio":
    ax.set_title(f"{griega_sel} {_('griegas.portfolio_vs_spot')}", fontsize=12)
else:
    tp_lbl = _("griegas.call_and_put") if ambos_tipos else ("Call" if tipo == "C" else "Put")
    ax.set_title(f"{griega_sel} ({tp_lbl}) vs Spot", fontsize=12)

ax.legend(fontsize=8.5, loc="best")
ax.grid(True, alpha=0.2)
ax.autoscale_view()
plt.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ════════════════════════════════════════════════════════════════════════════
# PANEL PUNTUAL — todas las griegas en S actual
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("griegas.panel_title", s=f"{S_actual:.2f}"))

def _all_greeks_single(tp, K_leg, T_leg, sigma_leg):
    row = {}
    for gn, gf in _GREEK_FUNCS.items():
        try:
            if gn == "Elasticity":
                V = opcion_europea_bs(tp, S_actual, K_leg, T_leg, r, sigma_leg, div)
                row[gn] = S_actual * delta_bs(tp, S_actual, K_leg, T_leg, r, sigma_leg, div) / V if V > 0 else np.nan
            else:
                row[gn] = gf(tp, S_actual, K_leg, T_leg, r, sigma_leg, div)
        except Exception:
            row[gn] = np.nan
    return row

def _fmt_g(v):
    return f"{v:.5f}" if np.isfinite(v) else "—"

panel_rows = []  # list of dicts for st.dataframe
_col_greek = _("griegas.greek")

if modo == "Opción única":
    if ambos_tipos:
        row_c = _all_greeks_single("C", K, T, sigma)
        row_p = _all_greeks_single("P", K, T, sigma)
        for g in _GREEK_FUNCS:
            panel_rows.append({_col_greek: g, "Call": _fmt_g(row_c[g]), "Put": _fmt_g(row_p[g])})
    else:
        row = _all_greeks_single(tipo, K, T, sigma)
        val_col = f"{'Call' if tipo=='C' else 'Put'} (K={K:.0f}, T={T}, σ={sigma})"
        for g in _GREEK_FUNCS:
            panel_rows.append({_col_greek: g, val_col: _fmt_g(row[g])})
else:
    total_row = {}
    for gn, gf in _GREEK_FUNCS.items():
        try:
            if gn == "Elasticity":
                V_tot = sum(l["qty"] * opcion_europea_bs(l["tipo"], S_actual, l["K"], l["T"], r, l["sigma"], div) for l in _legs_ss)
                D_tot = sum(l["qty"] * delta_bs(l["tipo"], S_actual, l["K"], l["T"], r, l["sigma"], div) for l in _legs_ss)
                total_row[gn] = S_actual * D_tot / V_tot if abs(V_tot) > 1e-10 else np.nan
            else:
                total_row[gn] = sum(
                    l["qty"] * gf(l["tipo"], S_actual, l["K"], l["T"], r, l["sigma"], div)
                    for l in _legs_ss
                )
        except Exception:
            total_row[gn] = np.nan

    leg_rows = {}
    for li, leg in enumerate(_legs_ss):
        tp_l = "Call" if leg["tipo"] == "C" else "Put"
        col_lbl = f"Leg {li+1} {tp_l} K={leg['K']:.0f} ×{leg['qty']:+d}"
        leg_rows[col_lbl] = _all_greeks_single(leg["tipo"], leg["K"], leg["T"], leg["sigma"])

    _col_total = _("griegas.total")
    for g in _GREEK_FUNCS:
        r_dict = {_col_greek: g, _col_total: _fmt_g(total_row[g])}
        for col_lbl, lr in leg_rows.items():
            r_dict[col_lbl] = _fmt_g(lr[g])
        panel_rows.append(r_dict)

st.dataframe(panel_rows, use_container_width=True, hide_index=True)

# ── Exportar ──────────────────────────────────────────────────────────────────
col_exp1, col_exp2 = st.columns(2)

# Export curva
with col_exp1:
    import pandas as _pd_exp
    df_curva = _pd_exp.DataFrame({_("griegas.spot_s"): S_vals})
    for label, vals, *_unused in curves:
        df_curva[label] = vals
    buf1 = io.BytesIO()
    df_curva.to_excel(buf1, index=False, sheet_name=griega_sel[:31], engine="openpyxl")
    buf1.seek(0)
    fn1 = f"griega_{griega_sel.replace(' ', '_')}_curva.xlsx"
    st.download_button(f"📥 {_('griegas.export_curve')}", data=buf1, file_name=fn1,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key="griegas_export_curva")

# Export panel puntual
with col_exp2:
    df_panel_exp = _pd_exp.DataFrame(panel_rows)
    buf2 = io.BytesIO()
    df_panel_exp.to_excel(buf2, index=False, sheet_name=_("griegas.sheet_puntual"), engine="openpyxl")
    buf2.seek(0)
    fn2 = f"griegas_panel_S{S_actual:.0f}.xlsx"
    st.download_button(f"📥 {_('griegas.export_panel')}", data=buf2, file_name=fn2,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       key="griegas_export_panel")
