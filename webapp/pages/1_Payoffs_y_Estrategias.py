# -*- coding: utf-8 -*-
"""Payoffs y Estrategias - Calcula precios de opciones y visualiza payoffs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import io
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from i18n import _


def _me_label(key: str, default: str) -> str:
    """Traduce key; si no existe, devuelve default (evita meta-nombres en UI)."""
    t = _(key)
    return default if t == key else t
from Codigo.pricing import (
    opcion_europea_bs,
    opcion_europea_bin,
    opcion_europea_mc,
    opcion_europea_fd,
    opcion_americana_bin,
    opcion_americana_fd,
    opcion_americana_bs,
    opcion_americana_mc,
    precio_estrategia,
    precio_estrategia_nombre,
    ESTRATEGIA_PIERNAS,
)
from Codigo.analytics.payoffs import (
    payoff_call, payoff_put,
    payoff_BullCS, payoff_BearCS, payoff_BullPS, payoff_BearPS,
    payoff_straddle, payoff_strangle,
    payoff_short_straddle, payoff_short_strangle,
    payoff_combo, payoff_collar, payoff_box,
    payoff_covered_call, payoff_protective_put,
    payoff_ratio_spread,
    payoff_CButterflyS, payoff_PButterflyS,
    payoff_iron_condor, payoff_iron_butterfly, payoff_condor,
    payoff_digital_call, payoff_digital_put,
    payoff_asian_call, payoff_asian_put,
    payoff_barrier_up_in_call, payoff_barrier_up_out_call,
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
    div[class*="block-container"], div[class*="BlockContainer"] { max-width: none !important; }
</style>
""", unsafe_allow_html=True)

st.title(_("me.title"))

# ── Datos estáticos ───────────────────────────────────────────────────────────
PAYOFFS_EXPLORER = {
    "Vanilla":     {"Call": payoff_call, "Put": payoff_put},
    "Estrategias": {
        "Bull Call Spread": payoff_BullCS,  "Bear Call Spread": payoff_BearCS,
        "Bull Put Spread":  payoff_BullPS,  "Bear Put Spread":  payoff_BearPS,
        "Straddle":         payoff_straddle,"Short Straddle":   payoff_short_straddle,
        "Strangle":         payoff_strangle,"Short Strangle":   payoff_short_strangle,
        "Combo":            payoff_combo,   "Collar":           payoff_collar,
        "Box":              payoff_box,     "Covered Call":     payoff_covered_call,
        "Protective Put":   payoff_protective_put, "Ratio Spread": payoff_ratio_spread,
        "Call Butterfly":   payoff_CButterflyS, "Put Butterfly": payoff_PButterflyS,
        "Iron Butterfly":   payoff_iron_butterfly, "Iron Condor": payoff_iron_condor,
        "Condor":           payoff_condor,
    },
    "Digitales": {"Digital Call": payoff_digital_call, "Digital Put": payoff_digital_put},
    "Asian":     {"Asian Call": payoff_asian_call, "Asian Put": payoff_asian_put},
    "Barrier":   {"Up-and-In Call": payoff_barrier_up_in_call, "Up-and-Out Call": payoff_barrier_up_out_call},
}

ESTRATEGIA_EXPLICACION = {
    "straddle":         "**Payoff:** Call(K) + Put(K). Compra call y put al mismo strike. **K:** strike común.",
    "short_straddle":   "**Payoff:** -(Call(K) + Put(K)). Vende call y put al mismo strike. **K:** strike común.",
    "covered_call":     "**Payoff:** -Call(K). Vende call cubierta (subyacente + short call). **K:** strike del call.",
    "protective_put":   "**Payoff:** +Put(K). Compra put para proteger subyacente. **K:** strike del put.",
    "strangle":         "**Payoff:** Call(K1) + Put(K2). K1 > K2, ambas OTM. **K1:** call, **K2:** put.",
    "short_strangle":   "**Payoff:** -(Call(K1) + Put(K2)). Vende call y put OTM. **K1:** call, **K2:** put.",
    "combo":            "**Payoff:** Call(K2) - Put(K1). Risk reversal. **K1 < K2**.",
    "collar":           "**Payoff:** Put(K1) - Call(K2). Protege con put, limita upside con call. **K1 < K2**.",
    "box":              "**Payoff:** constante K2-K1 (arbitraje). **K1 < K2**.",
    "bull_call_spread": "**Payoff:** Call(K1) - Call(K2). Alcista. **K1 < K2**.",
    "bear_call_spread": "**Payoff:** Call(K2) - Call(K1). Bajista. **K1 < K2**.",
    "bull_put_spread":  "**Payoff:** Put(K1) - Put(K2). Alcista. **K1 < K2**.",
    "bear_put_spread":  "**Payoff:** Put(K2) - Put(K1). Bajista. **K1 < K2**.",
    "ratio_spread":     "**Payoff:** n1·Call(K1) - n2·Call(K2). **K1 < K2**; n1 comprado, n2 vendidos.",
    "call_butterfly":   "**Payoff:** Call(K1) - 2·Call(K2) + Call(K3). **K1 < K2 < K3**, K2 cuerpo ATM.",
    "put_butterfly":    "**Payoff:** Put(K1) - 2·Put(K2) + Put(K3). **K1 < K2 < K3**, K2 cuerpo.",
    "iron_butterfly":   "**Payoff:** Put(K1)-Put(K2)+Call(K3)-Call(K2). **K1<K2<K3**, K2 cuerpo.",
    "iron_condor":      "**Payoff:** Put(K1)-Put(K2)-Call(K3)+Call(K4). **K1<K2<K3<K4**, rango K2-K3.",
    "condor":           "**Payoff:** Call(K1)-Call(K2)-Call(K3)+Call(K4). **K1<K2<K3<K4**, rango K2-K3.",
}

PAYOFF_TO_EXPLICACION = {
    "Bull Call Spread": "bull_call_spread", "Bear Call Spread": "bear_call_spread",
    "Bull Put Spread":  "bull_put_spread",  "Bear Put Spread":  "bear_put_spread",
    "Straddle":         "straddle",         "Short Straddle":   "short_straddle",
    "Strangle":         "strangle",         "Short Strangle":   "short_strangle",
    "Combo":            "combo",            "Collar":           "collar",
    "Box":              "box",              "Covered Call":     "covered_call",
    "Protective Put":   "protective_put",   "Ratio Spread":     "ratio_spread",
    "Call Butterfly":   "call_butterfly",   "Put Butterfly":    "put_butterfly",
    "Iron Butterfly":   "iron_butterfly",   "Iron Condor":      "iron_condor",
    "Condor":           "condor",
}

_NEEDS_STEPS = {"Binomial", "Monte Carlo", "Diferencias finitas"}
_ALL_MODELS  = ["Black-Scholes", "Binomial", "Monte Carlo", "Diferencias finitas"]

_PRICERS_EUR = {
    "Black-Scholes":       lambda tp, s, k, t, rv, sg, dv, ps: opcion_europea_bs(tp, s, k, t, rv, sg, dv),
    "Binomial":            lambda tp, s, k, t, rv, sg, dv, ps: opcion_europea_bin(tp, s, k, t, rv, sg, dv, int(ps)),
    "Monte Carlo":         lambda tp, s, k, t, rv, sg, dv, ps: opcion_europea_mc(tp, s, k, t, rv, sg, dv, int(ps)),
    "Diferencias finitas": lambda tp, s, k, t, rv, sg, dv, ps: opcion_europea_fd(tp, s, k, t, rv, sg, dv, M=max(50, min(300, int(ps)))),
}
_PRICERS_AME = {
    "Black-Scholes":       lambda tp, s, k, t, rv, sg, dv, ps: opcion_americana_bs(tp, s, k, t, rv, sg, dv),
    "Binomial":            lambda tp, s, k, t, rv, sg, dv, ps: opcion_americana_bin(tp, s, k, t, rv, sg, dv, int(ps)),
    "Monte Carlo":         lambda tp, s, k, t, rv, sg, dv, ps: opcion_americana_mc(tp, s, k, t, rv, sg, dv, int(ps)),
    "Diferencias finitas": lambda tp, s, k, t, rv, sg, dv, ps: opcion_americana_fd(tp, s, k, t, rv, sg, dv, M=max(50, min(300, int(ps)))),
}

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "me_precio_vanilla": None,
    "me_tabla_comp":     None,
    "me_precio_estr":    None,
    "me_modelo_usado":   None,
    "me_ejercicio_usado": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def _find_breakevens(S_range, payoff_vals):
    """Cruces por cero del payoff (interpolación lineal)."""
    bes = []
    pv = np.array(payoff_vals, dtype=float)
    for i in range(len(pv) - 1):
        if np.isfinite(pv[i]) and np.isfinite(pv[i + 1]):
            if pv[i] * pv[i + 1] < 0:
                be = S_range[i] - pv[i] * (S_range[i + 1] - S_range[i]) / (pv[i + 1] - pv[i])
                bes.append(float(be))
    return bes


def _call_pricer(pricers_dict, modelo, tipo, S, K, T, r, sigma, div, pasos):
    try:
        return float(pricers_dict[modelo](tipo, S, K, T, r, sigma, div, pasos))
    except Exception as exc:
        return str(exc)


# ════════════════════════════════════════════════════════════════════════════
# PARÁMETROS — 2 filas
# ════════════════════════════════════════════════════════════════════════════
with st.expander(f"📖 {_('me.how_to_use')}", expanded=False):
    st.markdown(f"""
    1. {_("me.help_1")}
    2. {_("me.help_2")}
    3. {_("me.help_3")}
    4. {_("me.help_4")}
    """)

st.subheader(_("me.params"))
row1 = st.columns(4)
with row1[0]: S     = st.number_input(_("prop.s_spot"),       value=100.0, min_value=0.1,  step=1.0)
with row1[1]: K     = st.number_input(_("prop.k_strike"),     value=100.0, min_value=0.1,  step=1.0)
with row1[2]: T     = st.number_input(_("prop.t_years"),     value=1.0,   min_value=0.01, step=0.1)
with row1[3]: r     = st.number_input(_("prop.r_rate"),       value=0.05,  min_value=0.0,  max_value=1.0, format="%.3f")

row2 = st.columns(4)
with row2[0]: sigma = st.number_input(_("prop.sigma_vol"),    value=0.25,  min_value=0.01, max_value=2.0, format="%.3f")
with row2[1]: div   = st.number_input(_("prop.div_dividends"),value=0.0,  min_value=0.0,  max_value=1.0, format="%.3f")
with row2[2]: tipo  = st.radio(_("me.type"), ["C", "P"], horizontal=True)
with row2[3]:
    _ej_opts = {"Europea": "me.european", "Americana": "me.american"}
    ejercicio = st.radio(_("me.exercise"), options=["Europea", "Americana"],
                         format_func=lambda x: _(_ej_opts[x]), horizontal=True)

pricers = _PRICERS_EUR if ejercicio == "Europea" else _PRICERS_AME

# ════════════════════════════════════════════════════════════════════════════
# MODO: Vanilla o Estrategia
# ════════════════════════════════════════════════════════════════════════════
st.divider()
modo = st.radio(_("me.mode"), options=["Vanilla", "Estrategia"],
                format_func=lambda x: "Vanilla" if x == "Vanilla" else _("me.strategy"), horizontal=True)

# ── VANILLA ──────────────────────────────────────────────────────────────────
if modo == "Vanilla":
    col_mod, col_pasos, col_btn, col_cmp = st.columns([3, 2, 1, 2])
    with col_mod:
        modelo = st.selectbox(_("me.model"), _ALL_MODELS)
    with col_pasos:
        if modelo in _NEEDS_STEPS:
            pasos = st.number_input(_("me.steps"), value=1000, min_value=10, step=100)
        else:
            pasos = 1000
            st.caption(_("me.steps_na"))
    with col_btn:
        st.write("")
        calc_v = st.button(_("me.calculate"), type="primary", use_container_width=True)
    with col_cmp:
        st.write("")
        comp_v = st.button(_("me.compare_all"), use_container_width=True)

    if calc_v:
        res = _call_pricer(pricers, modelo, tipo, S, K, T, r, sigma, div, pasos)
        st.session_state.me_precio_vanilla  = res
        st.session_state.me_modelo_usado    = modelo
        st.session_state.me_ejercicio_usado = ejercicio
        st.session_state.me_tabla_comp      = None

    if comp_v:
        rows = []
        with st.spinner(_("me.calculating_all")):
            for m in _ALL_MODELS:
                ps = pasos if m in _NEEDS_STEPS else 1000
                precio = _call_pricer(pricers, m, tipo, S, K, T, r, sigma, div, ps)
                rows.append({"Modelo": m, "Precio": precio})
        st.session_state.me_tabla_comp      = rows
        st.session_state.me_precio_vanilla  = None
        st.session_state.me_ejercicio_usado = ejercicio

    # Mostrar resultado individual
    if st.session_state.me_precio_vanilla is not None:
        res   = st.session_state.me_precio_vanilla
        mod_u = st.session_state.me_modelo_usado
        ej_u  = st.session_state.me_ejercicio_usado
        tipo_label = "Call" if tipo == "C" else "Put"
        if isinstance(res, float):
            st.success(
                f"**{mod_u}** · {ej_u} · {tipo_label} → **{_('me.price')}: {res:.4f}**"
            )
        else:
            st.error(f"{_('me.error')} ({mod_u}): {res}")

    # Tabla comparativa
    if st.session_state.me_tabla_comp is not None:
        ej_u = st.session_state.me_ejercicio_usado
        tipo_label = "Call" if tipo == "C" else "Put"
        _ej_disp = _("me.european") if ej_u == "Europea" else _("me.american")
        st.markdown(f"**{_('me.compare_title', exercise=_ej_disp, type=tipo_label)}**  (S={S}, K={K}, T={T}, r={r}, σ={sigma}, div={div})")
        comp_rows = []
        _col_model, _col_price = _("me.model"), _("me.price")
        for row in st.session_state.me_tabla_comp:
            r_copy = {_col_model: row.get("Modelo"), _col_price: row.get("Precio")}
            p = r_copy[_col_price]
            r_copy[_col_price] = f"{p:.4f}" if isinstance(p, float) else f"⚠ {p}"
            comp_rows.append(r_copy)
        st.dataframe(comp_rows, use_container_width=True, hide_index=True)

# ── ESTRATEGIA ────────────────────────────────────────────────────────────────
else:
    col_estr, col_btn_e = st.columns([5, 1])
    with col_estr:
        estrategia = st.selectbox(_("me.strategy"), list(ESTRATEGIA_PIERNAS.keys()))
    with col_btn_e:
        st.write("")
        calc_e = st.button(_("me.calc_strategy"), type="primary", use_container_width=True)

    # Inputs de strikes según estrategia
    if estrategia in ("straddle", "short_straddle", "covered_call", "protective_put"):
        c1, *_unused = st.columns(4)
        with c1: K1 = st.number_input("K", value=K, min_value=0.1)
        kwargs = {"K": K1}
    elif estrategia in ("strangle", "short_strangle", "combo", "collar", "box",
                        "bull_call_spread", "bear_call_spread", "bull_put_spread", "bear_put_spread"):
        c1, c2, *_unused = st.columns(4)
        with c1: K1 = st.number_input("K1", value=round(K * 0.9, 2), min_value=0.1)
        with c2: K2 = st.number_input("K2", value=round(K * 1.1, 2), min_value=0.1)
        kwargs = {"K1": K1, "K2": K2}
    elif estrategia == "ratio_spread":
        c1, c2, c3, c4 = st.columns(4)
        with c1: K1 = st.number_input("K1", value=round(K * 0.95, 2), min_value=0.1)
        with c2: K2 = st.number_input("K2", value=round(K * 1.05, 2), min_value=0.1)
        with c3: n1 = st.number_input("n1", value=1, min_value=1)
        with c4: n2 = st.number_input("n2", value=2, min_value=1)
        kwargs = {"K1": K1, "K2": K2, "n1": int(n1), "n2": int(n2)}
    elif estrategia in ("call_butterfly", "put_butterfly", "iron_butterfly"):
        c1, c2, c3, _unused = st.columns(4)
        with c1: K1 = st.number_input("K1", value=round(K * 0.9, 2), min_value=0.1)
        with c2: K2 = st.number_input("K2", value=K, min_value=0.1)
        with c3: K3 = st.number_input("K3", value=round(K * 1.1, 2), min_value=0.1)
        kwargs = {"K1": K1, "K2": K2, "K3": K3}
    else:  # iron_condor, condor
        c1, c2, c3, c4 = st.columns(4)
        with c1: K1 = st.number_input("K1", value=round(K * 0.85, 2), min_value=0.1)
        with c2: K2 = st.number_input("K2", value=round(K * 0.95, 2), min_value=0.1)
        with c3: K3 = st.number_input("K3", value=round(K * 1.05, 2), min_value=0.1)
        with c4: K4 = st.number_input("K4", value=round(K * 1.15, 2), min_value=0.1)
        kwargs = {"K1": K1, "K2": K2, "K3": K3, "K4": K4}

    if estrategia in ESTRATEGIA_EXPLICACION:
        st.info(ESTRATEGIA_EXPLICACION[estrategia])

    if calc_e:
        try:
            precio_e = precio_estrategia_nombre(estrategia, S, T, r, sigma, div, **kwargs)
            st.session_state.me_precio_estr = float(precio_e)
        except Exception as exc:
            st.session_state.me_precio_estr = str(exc)

    if st.session_state.me_precio_estr is not None:
        res_e = st.session_state.me_precio_estr
        nombre_label = estrategia.replace("_", " ").title()
        if isinstance(res_e, float):
            st.success(f"**{nombre_label}** → **{_('me.price')}: {res_e:.4f}**")
        else:
            st.error(f"{_('me.error')}: {res_e}")

# ════════════════════════════════════════════════════════════════════════════
# PAYOFF Y ESTRATEGIAS
# ════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander(f"📖 {_('me.payoff_how_to')}", expanded=False):
    st.markdown(_("me.payoff_help"))

st.subheader(_("me.payoff_strategies"))

_CAT_DISPLAY = {"Vanilla": "me.cat_vanilla", "Estrategias": "me.cat_strategies",
                "Digitales": "me.cat_digitals", "Asian": "me.cat_asian", "Barrier": "me.cat_barrier"}
cat_col, payoff_col, smin_col, smax_col = st.columns([2, 3, 1, 1])
with cat_col:
    categoria_payoff = st.selectbox(_("me.category"), options=list(PAYOFFS_EXPLORER.keys()),
                                   format_func=lambda k: _(_CAT_DISPLAY.get(k, k)))
with payoff_col:
    payoff_name = st.selectbox("Payoff", list(PAYOFFS_EXPLORER[categoria_payoff].keys()))
with smin_col:
    S_min_plot = st.number_input(_("me.s_min"), value=max(1.0, S * 0.5), key="payoff_Smin")
with smax_col:
    S_max_plot = st.number_input(_("me.s_max"), value=S * 1.5, key="payoff_Smax")

payoff_func_plot = PAYOFFS_EXPLORER[categoria_payoff][payoff_name]

# Explicación de la estrategia
if categoria_payoff == "Estrategias" and payoff_name in PAYOFF_TO_EXPLICACION:
    key_expl = PAYOFF_TO_EXPLICACION[payoff_name]
    if key_expl in ESTRATEGIA_EXPLICACION:
        st.info(ESTRATEGIA_EXPLICACION[key_expl])

# Inputs de parámetros del payoff + K base siempre visible
K_plot = st.number_input(_("me.k_base"), value=K, min_value=1.0, key="payoff_K")
plot_kwargs = {"K": K_plot}
strike_lines = [K_plot]  # strikes a marcar con líneas verticales

if payoff_func_plot in (payoff_straddle, payoff_short_straddle,
                        payoff_covered_call, payoff_protective_put):
    strike_lines = [K_plot]
    plot_kwargs  = {"K": K_plot}

elif payoff_func_plot in (
    payoff_BullCS, payoff_BearCS, payoff_BullPS, payoff_BearPS,
    payoff_strangle, payoff_short_strangle, payoff_combo, payoff_collar, payoff_box,
):
    c1, c2 = st.columns(2)
    with c1: K1_plot = st.number_input("K1", value=round(K * 0.9, 2), min_value=0.1, key="payoff_K1")
    with c2: K2_plot = st.number_input("K2", value=round(K * 1.1, 2), min_value=0.1, key="payoff_K2")
    plot_kwargs  = {"K1": K1_plot, "K2": K2_plot}
    strike_lines = [K1_plot, K2_plot]

elif payoff_func_plot == payoff_ratio_spread:
    c1, c2, c3, c4 = st.columns(4)
    with c1: K1_plot = st.number_input("K1", value=round(K * 0.95, 2), min_value=0.1, key="payoff_K1")
    with c2: K2_plot = st.number_input("K2", value=round(K * 1.05, 2), min_value=0.1, key="payoff_K2")
    with c3: n1_plot = st.number_input("n1", value=1, min_value=1, key="payoff_n1")
    with c4: n2_plot = st.number_input("n2", value=2, min_value=1, key="payoff_n2")
    plot_kwargs  = {"K1": K1_plot, "K2": K2_plot, "n1": int(n1_plot), "n2": int(n2_plot)}
    strike_lines = [K1_plot, K2_plot]

elif payoff_func_plot in (payoff_CButterflyS, payoff_PButterflyS, payoff_iron_butterfly):
    c1, c2, c3 = st.columns(3)
    with c1: K1_plot = st.number_input("K1", value=round(K * 0.9, 2), min_value=0.1, key="payoff_K1")
    with c2: K2_plot = st.number_input("K2", value=K, min_value=0.1, key="payoff_K2")
    with c3: K3_plot = st.number_input("K3", value=round(K * 1.1, 2), min_value=0.1, key="payoff_K3")
    plot_kwargs  = {"K1": K1_plot, "K2": K2_plot, "K3": K3_plot}
    strike_lines = [K1_plot, K2_plot, K3_plot]

elif payoff_func_plot in (payoff_iron_condor, payoff_condor):
    c1, c2, c3, c4 = st.columns(4)
    with c1: K1_plot = st.number_input("K1", value=round(K * 0.85, 2), min_value=0.1, key="payoff_K1")
    with c2: K2_plot = st.number_input("K2", value=round(K * 0.95, 2), min_value=0.1, key="payoff_K2")
    with c3: K3_plot = st.number_input("K3", value=round(K * 1.05, 2), min_value=0.1, key="payoff_K3")
    with c4: K4_plot = st.number_input("K4", value=round(K * 1.15, 2), min_value=0.1, key="payoff_K4")
    plot_kwargs  = {"K1": K1_plot, "K2": K2_plot, "K3": K3_plot, "K4": K4_plot}
    strike_lines = [K1_plot, K2_plot, K3_plot, K4_plot]

elif payoff_func_plot in (payoff_digital_call, payoff_digital_put):
    Q_plot = st.number_input(_("me.q_digital"), value=10.0, key="payoff_Q")
    plot_kwargs  = {"K": K_plot, "Q": Q_plot}
    strike_lines = [K_plot]

elif categoria_payoff == "Barrier":
    c1, c2 = st.columns(2)
    with c1: B_plot = st.number_input(_("me.b_barrier"), value=round(K * 1.2, 2), min_value=0.1, key="payoff_B")
    with c2: barrier_hit = st.checkbox(_("me.barrier_hit"), value=True, key="payoff_barrier_hit")
    plot_kwargs  = {"K": K_plot, "B": B_plot, "barrier_hit": barrier_hit}
    strike_lines = [K_plot, B_plot]

# ── Prima automática ─────────────────────────────────────────────────────────
_prima_auto = 0.0
try:
    if categoria_payoff == "Vanilla":
        _tp = "C" if payoff_name == "Call" else "P"
        _prima_auto = float(opcion_europea_bs(_tp, S, K_plot, T, r, sigma, div))
    elif categoria_payoff == "Estrategias" and payoff_name in PAYOFF_TO_EXPLICACION:
        _key = PAYOFF_TO_EXPLICACION[payoff_name]
        _prima_auto = float(precio_estrategia_nombre(_key, S, T, r, sigma, div, **plot_kwargs))
except Exception:
    _prima_auto = 0.0

col_prima, col_prima_info = st.columns([2, 3])
with col_prima:
    prima = st.number_input(
        _("me.premium_paid"),
        value=round(float(_prima_auto), 4),
        step=0.01, format="%.4f", key="payoff_prima",
        help=_("me.premium_help"),
    )
prima_fv = prima * np.exp(r * T)
with col_prima_info:
    st.info(
        f"**{_('me.carry_premium')}**  \n"
        f"FV(C) = C · e^(r·T) = {prima:.4f} · e^({r:.3f}·{T:.2f}) = **{prima_fv:.4f}**  \n"
        f"**{_('me.pnl_formula', fv=f'{prima_fv:.4f}')}**"
    )

# ── Gráfico del payoff y P&L ─────────────────────────────────────────────────
if S_min_plot >= S_max_plot:
    st.error(_("me.s_min_max_error"))
else:
    S_range = np.linspace(S_min_plot, S_max_plot, 300)
    try:
        payoff_vals = np.array(payoff_func_plot(S_range, **plot_kwargs), dtype=float)
        pnl_vals    = payoff_vals - prima_fv   # P&L = payoff − FV(prima)

        fig, ax = plt.subplots(figsize=(11, 5), dpi=110)

        # Área coloreada según P&L
        ax.fill_between(S_range, pnl_vals, 0,
                        where=pnl_vals >= 0, alpha=0.13, color="#2ca02c", interpolate=True)
        ax.fill_between(S_range, pnl_vals, 0,
                        where=pnl_vals < 0,  alpha=0.13, color="#d62728", interpolate=True)

        # Payoff al vencimiento (línea punteada gris, referencia)
        ax.plot(S_range, payoff_vals, color="#aaaaaa", linewidth=1.3,
                linestyle="--", label=_("me.payoff_no_cost"), zorder=2)

        # P&L (línea principal)
        ax.plot(S_range, pnl_vals, color="#1f77b4", linewidth=2.3,
                label=_("me.pnl_premium", fv=f"{prima_fv:.3f}"), zorder=3)

        ax.axhline(0, color="gray", linewidth=0.9)

        # Líneas verticales en strikes
        strike_colors = ["#e8750a", "#9467bd", "#17becf", "#bcbd22"]
        for i, sk in enumerate(strike_lines):
            if S_min_plot <= sk <= S_max_plot:
                col_c = strike_colors[i % len(strike_colors)]
                ax.axvline(sk, color=col_c, linewidth=1.2, linestyle="--", alpha=0.8)
                _labels = ["K₁", "K₂", "K₃", "K₄"]
                _lbl = _labels[i] if i < len(_labels) else f"K{i+1}"
                ax.text(sk, ax.get_ylim()[1] if ax.get_ylim()[1] != 0 else 1,
                        f" {_lbl}={sk:.1f}",
                        color=col_c, fontsize=8, va="top", ha="left")

        # S actual
        if S_min_plot <= S <= S_max_plot:
            ax.axvline(S, color="#2ca02c", linewidth=1.4, linestyle=":",
                       label=_("me.s_current", s=f"{S:.1f}"))

        # Break-even del P&L
        breakevens_pnl = _find_breakevens(S_range, pnl_vals)
        for be in breakevens_pnl:
            ax.axvline(be, color="#d62728", linewidth=1.0, linestyle="-.", alpha=0.8)
            ax.annotate(
                f"BE\n{be:.2f}",
                xy=(be, 0), xytext=(0, 14), textcoords="offset points",
                ha="center", fontsize=7.5, color="#d62728",
                arrowprops=dict(arrowstyle="-", color="#d62728", lw=0.8),
            )

        # Líneas horizontales max P&L / min P&L
        valid_pnl = pnl_vals[np.isfinite(pnl_vals)]
        if len(valid_pnl):
            max_pnl = valid_pnl.max()
            min_pnl = valid_pnl.min()
            if np.isfinite(max_pnl) and abs(max_pnl) > 1e-6:
                ax.axhline(max_pnl, color="#2ca02c", linewidth=0.8, linestyle=":", alpha=0.7)
                ax.text(S_max_plot, max_pnl, f"  +{max_pnl:.2f}",
                        color="#2ca02c", fontsize=8, va="bottom")
            if np.isfinite(min_pnl) and abs(min_pnl) > 1e-6:
                ax.axhline(min_pnl, color="#d62728", linewidth=0.8, linestyle=":", alpha=0.7)
                ax.text(S_max_plot, min_pnl, f"  {min_pnl:.2f}",
                        color="#d62728", fontsize=8, va="top")

        ax.set_xlabel(_("me.xlabel_underlying"), fontsize=11)
        ax.set_ylabel(_("me.ylabel_pnl"), fontsize=11)
        ax.set_title(_("me.title_pnl", name=payoff_name), fontsize=12)
        ax.legend(fontsize=9, loc="best")
        ax.grid(True, alpha=0.2)
        ax.autoscale_view()
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        # ── Resumen analítico del P&L ─────────────────────────────────────
        valid_idx = np.where(np.isfinite(pnl_vals))[0]
        if len(valid_idx):
            max_idx  = valid_idx[np.argmax(pnl_vals[valid_idx])]
            min_idx  = valid_idx[np.argmin(pnl_vals[valid_idx])]
            max_gain_val = float(pnl_vals[max_idx]);  max_gain_s = float(S_range[max_idx])
            max_loss_val = float(pnl_vals[min_idx]);  max_loss_s = float(S_range[min_idx])

            boundaries = sorted([float(S_min_plot)] + breakevens_pnl + [float(S_max_plot)])
            gain_ivs, loss_ivs = [], []
            for bi in range(len(boundaries) - 1):
                mid = (boundaries[bi] + boundaries[bi + 1]) / 2
                idx_mid = int(np.argmin(np.abs(S_range - mid)))
                pv_mid = pnl_vals[idx_mid]
                if np.isfinite(pv_mid):
                    if pv_mid > 0:
                        gain_ivs.append((boundaries[bi], boundaries[bi + 1]))
                    elif pv_mid < 0:
                        loss_ivs.append((boundaries[bi], boundaries[bi + 1]))

            _concept, _valor, _nivel = _("me.concept"), _("me.value"), _("me.s_level")
            rows_summary = []
            rows_summary.append({
                _concept: _("me.max_gain"),
                _valor:   f"+{max_gain_val:.3f}" if max_gain_val > 0 else "—",
                _nivel:   f"{max_gain_s:.2f}"   if max_gain_val > 0 else "—",
            })
            rows_summary.append({
                _concept: _("me.max_loss"),
                _valor:   f"{max_loss_val:.3f}"  if max_loss_val < 0 else "—",
                _nivel:   f"{max_loss_s:.2f}"   if max_loss_val < 0 else "—",
            })
            if gain_ivs:
                for gi, (s_lo, s_hi) in enumerate(gain_ivs):
                    label = _("me.gain_zone_n", n=gi+1) if len(gain_ivs) > 1 else _("me.gain_zone")
                    rows_summary.append({_concept: label, _valor: "> 0", _nivel: f"[{s_lo:.2f}, {s_hi:.2f}]"})
            else:
                rows_summary.append({_concept: _("me.gain_zone"), _valor: _("me.none"), _nivel: "—"})

            if loss_ivs:
                for li, (s_lo, s_hi) in enumerate(loss_ivs):
                    label = _("me.loss_zone_n", n=li+1) if len(loss_ivs) > 1 else _("me.loss_zone")
                    rows_summary.append({_concept: label, _valor: "< 0", _nivel: f"[{s_lo:.2f}, {s_hi:.2f}]"})
            else:
                rows_summary.append({_concept: _("me.loss_zone"), _valor: _("me.none"), _nivel: "—"})

            if breakevens_pnl:
                for bei, be in enumerate(breakevens_pnl):
                    label = _("me.breakeven_n", n=bei+1) if len(breakevens_pnl) > 1 else _("me.breakeven")
                    rows_summary.append({_concept: label, _valor: "0", _nivel: f"{be:.3f}"})
            else:
                rows_summary.append({_concept: _("me.breakeven"), _valor: "—", _nivel: _("me.not_found_range")})

            st.markdown(f"**{_('me.summary_pnl', name=payoff_name)}**  "
                        f"_(prima pagada: {prima:.4f} → FV={prima_fv:.4f})_")
            st.dataframe(rows_summary, use_container_width=True, hide_index=True)

    except Exception as exc:
        st.warning(_("me.plot_error", exc=str(exc)))

# ════════════════════════════════════════════════════════════════════════════
# ESCENARIOS (Valor / P&L en S × tiempo)
# ════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader(_me_label("me.scenarios", "Escenarios"))

# Variables para escenarios (modo Estrategia no tiene modelo/pasos del bloque principal)
_modelo_init = modelo if modo == "Vanilla" else "Black-Scholes"
_pasos_init = pasos if modo == "Vanilla" else 1000
if modo == "Estrategia":
    estrategia_esc = estrategia
    kwargs_esc = kwargs
else:
    estrategia_esc = None
    kwargs_esc = {}

S_lo_me = max(1.0, S * 0.5)
S_hi_me = S * 1.5

# Grilla
me_eg1, me_eg2, me_eg3, me_eg4 = st.columns(4)
with me_eg1:
    n_cols_me = st.number_input(_me_label("me.esc_cols", "Columnas (tiempo)"), value=4, min_value=2, max_value=20, step=1, key="me_esc_ncol")
with me_eg2:
    n_rows_me = st.number_input(_me_label("me.esc_rows", "Filas (precio)"), value=11, min_value=3, max_value=51, step=2, key="me_esc_nrow")
with me_eg3:
    S_desde_me = st.number_input("S desde", value=round(S_lo_me, 1), min_value=0.1, step=1.0,
                                 format="%.1f", key="me_esc_s_desde")
with me_eg4:
    S_a_me = st.number_input("S hasta", value=round(S_hi_me, 1), min_value=0.1, step=1.0,
                             format="%.1f", key="me_esc_s_a")

# Modelo (para escenarios)
me_em1, me_em2, me_em3 = st.columns(3)
with me_em1:
    modelo_esc = st.selectbox(_("me.model"), _ALL_MODELS, key="me_esc_modelo",
                              index=_ALL_MODELS.index(_modelo_init) if _modelo_init in _ALL_MODELS else 0)
with me_em2:
    pasos_esc = st.number_input(_("me.steps"), value=_pasos_init, min_value=10, max_value=5000, step=100,
                                key="me_esc_pasos", disabled=(modelo_esc not in _NEEDS_STEPS))
with me_em3:
    M_me = st.number_input("M (FD)", value=150, min_value=20, max_value=500, step=10,
                           key="me_esc_M", disabled=(modelo_esc != "Diferencias finitas"))

# Pagado (costo teórico) — usa modelo/pasos seleccionados en escenarios
_pasos_pagado = int(M_me) if modelo_esc == "Diferencias finitas" else int(pasos_esc)
try:
    if modo == "Vanilla":
        pagado_me = float(st.session_state.get("me_precio_vanilla") or 0)
        if pagado_me == 0:
            res_p = _call_pricer(pricers, modelo_esc, tipo, S, K, T, r, sigma, div, _pasos_pagado)
            pagado_me = float(res_p) if isinstance(res_p, (int, float)) else 0.0
    else:
        pagado_me = float(st.session_state.get("me_precio_estr") or 0)
        if pagado_me == 0:
            pagado_me = float(precio_estrategia_nombre(estrategia_esc, S, T, r, sigma, div, **kwargs_esc))
except Exception:
    pagado_me = 0.0

_me_esc_params = (n_rows_me, n_cols_me, S_desde_me, S_a_me, modelo_esc, pasos_esc, M_me, r, div,
                  modo, tipo if modo == "Vanilla" else estrategia_esc,
                  K if modo == "Vanilla" else tuple(sorted(kwargs_esc.items())))
_me_stored = st.session_state.get("me_esc_params")
if _me_stored is not None and _me_esc_params != _me_stored:
    st.session_state.pop("me_esc_cached", None)
    st.session_state.pop("me_esc_params", None)
    st.session_state.pop("me_esc_result", None)

calc_me = st.button(
    _me_label("me.recalc_esc", "Recalcular escenarios") if st.session_state.get("me_esc_cached") else _me_label("me.calc_esc", "Calcular escenarios"),
    type="primary", key="me_calc_esc",
)
if calc_me:
    st.session_state["me_esc_cached"] = True
    st.session_state.pop("me_esc_result", None)

if not st.session_state.get("me_esc_cached"):
    st.info(_me_label("me.click_calc_esc", "Hacé clic en **Calcular escenarios** para ver la matriz."))
    st.stop()

today_me = datetime.now().date()
T_max_me = T
mat_me = df_esc_me = df_pnl_me = date_cols_me = unique_cols_me = row_labels_me = n_cols_actual_me = None
if _me_stored is not None and _me_esc_params == _me_stored:
    _cached_me = st.session_state.get("me_esc_result")
    if _cached_me is not None:
        mat_me, df_esc_me, df_pnl_me, date_cols_me, unique_cols_me, row_labels_me, n_cols_actual_me = _cached_me

def _unique_labels_me(labels):
    seen = {}
    result = []
    for lb in labels:
        if lb in seen:
            seen[lb] += 1
            result.append(f"{lb}_{seen[lb]}")
        else:
            seen[lb] = 0
            result.append(lb)
    return result

if mat_me is None:
    st.session_state["me_esc_params"] = _me_esc_params
    S_vals_me = np.linspace(min(S_desde_me, S_a_me), max(S_desde_me, S_a_me), int(n_rows_me))
    t_vals_me = [T_max_me * (n_cols_me - 1 - i) / max(1, n_cols_me - 1) for i in range(n_cols_me)]
    if n_cols_me >= 2 and T_max_me / max(1, n_cols_me - 1) > 1e-6:
        t_vals_me = t_vals_me[:-1] + [T_max_me / max(1, n_cols_me - 1) * 0.5, 0.0]
    n_cols_actual_me = len(t_vals_me)

    expiry_me = today_me + timedelta(days=int(T_max_me * 365))
    date_cols_me = []
    for j in range(n_cols_actual_me):
        frac = j / (n_cols_actual_me - 1) if n_cols_actual_me > 1 else 1
        d = today_me + timedelta(days=int(T_max_me * 365 * (1 - frac)))
        date_cols_me.append(d.strftime("%d/%m/%y"))

    _pasos_arg = int(M_me) if modelo_esc == "Diferencias finitas" else int(pasos_esc)
    def _price_me(S_val, T_eff):
        if modo == "Vanilla":
            res = _call_pricer(pricers, modelo_esc, tipo, S_val, K, T_eff, r, sigma, div, _pasos_arg)
            return float(res) if isinstance(res, (int, float)) else 0.0
        piernas_me = ESTRATEGIA_PIERNAS[estrategia_esc](**kwargs_esc)
        def _pricer_me(tp, s, k, t, rv, sg, dv, **kw):
            res = _call_pricer(pricers, modelo_esc, tp, s, k, t, rv, sg, dv, _pasos_arg)
            return float(res) if isinstance(res, (int, float)) else 0.0
        return float(precio_estrategia(piernas_me, S_val, T_eff, r, sigma, div, pricer=_pricer_me))

    prog_me = st.progress(0, text=_("me.calculating"))
    mat_me = np.zeros((int(n_rows_me), n_cols_actual_me))
    total_me = int(n_rows_me) * n_cols_actual_me
    for i, S_val in enumerate(S_vals_me):
        for j, T_val in enumerate(t_vals_me):
            mat_me[i, j] = _price_me(S_val, T_val)
            idx = i * n_cols_actual_me + j
            if total_me > 0 and idx % max(1, total_me // 20) == 0:
                prog_me.progress(min(1.0, idx / total_me), text=f"Calculando... {idx}/{total_me}")
    prog_me.progress(1.0, text="Listo")
    prog_me.empty()

    unique_cols_me = _unique_labels_me(date_cols_me)
    row_labels_me = _unique_labels_me([f"S={s:.1f}" for s in S_vals_me])
    df_esc_me = pd.DataFrame(mat_me, index=row_labels_me, columns=unique_cols_me)
    df_esc_me = df_esc_me.iloc[::-1].round(1)
    df_pnl_me = (df_esc_me - pagado_me).round(1)
    st.session_state["me_esc_result"] = (mat_me, df_esc_me, df_pnl_me, date_cols_me, unique_cols_me, row_labels_me, n_cols_actual_me)

def _gradient_style_me(df, ref, fmt="{:.1f}"):
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

def _esc_column_config_me(cols, pct=False):
    fmt = "%.1f%%" if pct else "%.1f"
    return {c: st.column_config.NumberColumn(c, format=fmt) for c in cols}

costo_fv_me = pagado_me * np.exp(r * T_max_me) if pagado_me != 0 else 1.0
df_pct_pnl_me = (df_pnl_me / costo_fv_me * 100).round(1) if costo_fv_me != 0 else df_pnl_me * 0

_VISTA_OPTS_ME = {"PnL": "P&L (valor − pagado)", "Valor": "Valor de la estrategia", "%PnL": "%PnL (P&L / FV pagado)"}
tabla_vista_me = st.radio(
    "Vista",
    options=["PnL", "Valor", "%PnL"],
    format_func=lambda x: _VISTA_OPTS_ME[x],
    horizontal=True, index=0, key="me_esc_tabla_vista",
)
if tabla_vista_me == "Valor":
    df_show_me = df_esc_me
    ref_show_me = pagado_me
    fmt_show_me = "{:.1f}"
    pct_show_me = False
elif tabla_vista_me == "%PnL":
    df_show_me = df_pct_pnl_me
    ref_show_me = 0
    fmt_show_me = "{:.1f}%"
    pct_show_me = True
else:
    df_show_me = df_pnl_me
    ref_show_me = 0
    fmt_show_me = "{:.1f}"
    pct_show_me = False

st.dataframe(
    _gradient_style_me(df_show_me, ref_show_me, fmt=fmt_show_me),
    use_container_width=False,
    height=max(400, min(600, 32 * len(df_show_me) + 50)),
    column_config=_esc_column_config_me(unique_cols_me, pct=pct_show_me),
)

# Gráfico curvas P&L
st.markdown("**Curvas P&L vs S por fecha**")
colors_me = plt.cm.tab10(np.linspace(0, 1, n_cols_actual_me))
fig_me, ax_me = plt.subplots(figsize=(11, 4), dpi=100)
S_labels_me = [float(lbl.split("=")[1].split("_")[0]) for lbl in df_pnl_me.index
               if "=" in str(lbl) and "_" not in str(lbl).split("=")[1][:5]]
if len(S_labels_me) != len(df_pnl_me.index):
    S_labels_me = []
    for lbl in df_pnl_me.index:
        try:
            S_labels_me.append(float(str(lbl).split("=")[1].split("_")[0]))
        except Exception:
            S_labels_me.append(0.0)
for j_col, col_name in enumerate(unique_cols_me):
    vals_me = df_pnl_me[col_name].values
    disp_me = date_cols_me[j_col] if j_col < len(date_cols_me) else col_name
    lw_me = 2.4 if j_col == 0 else (2.0 if j_col == len(unique_cols_me) - 1 else 1.3)
    ls_me = "-" if j_col in (0, len(unique_cols_me) - 1) else "--"
    ax_me.plot(S_labels_me, vals_me, color=colors_me[j_col], linewidth=lw_me, linestyle=ls_me, label=disp_me)
ax_me.axhline(0, color="black", linewidth=0.8)
if min(S_desde_me, S_a_me) <= S <= max(S_desde_me, S_a_me):
    ax_me.axvline(S, color="#2ca02c", linewidth=1.2, linestyle="--", alpha=0.85, label=f"Spot={S:.1f}")
ax_me.axvline(K, color="#ff7f0e", linewidth=0.8, linestyle=":", alpha=0.6, label=f"K={K:.0f}")
ax_me.set_xlabel(_("me.xlabel_underlying"), fontsize=10)
ax_me.set_ylabel(_("me.ylabel_pnl"), fontsize=10)
titulo_me = (f"{'Call' if tipo == 'C' else 'Put'} K={K}" if modo == "Vanilla"
             else f"{estrategia_esc.replace('_', ' ').title()}")
ax_me.set_title(f"P&L en distintos momentos — {titulo_me}", fontsize=11)
ax_me.legend(fontsize=8, loc="best")
ax_me.grid(True, alpha=0.2)
plt.tight_layout()
st.pyplot(fig_me, use_container_width=True)
plt.close(fig_me)

# Exportar
buf_me = io.BytesIO()
with pd.ExcelWriter(buf_me, engine="openpyxl") as xl:
    df_esc_me.to_excel(xl, sheet_name="Valor estrategia")
    df_pnl_me.to_excel(xl, sheet_name="P&L")
    df_pct_pnl_me.to_excel(xl, sheet_name="%PnL")
buf_me.seek(0)
fn_me = f"me_escenarios_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
st.download_button("📥 Exportar escenarios a Excel", data=buf_me.getvalue(), file_name=fn_me,
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   key="me_export_esc")
