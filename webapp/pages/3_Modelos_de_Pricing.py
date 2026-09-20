# -*- coding: utf-8 -*-
"""
Modelos de Pricing — Comparación de modelos (BS, Binomial, MC, FD, BAW, …).

Sensibilidad del precio ante un parámetro, eligiendo una o más curvas
(ejercicio × modelo × Call/Put).
"""
import io
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from i18n import _
from Codigo.pricing import (
    opcion_europea_bs,
    opcion_europea_bin,
    opcion_europea_mc,
    opcion_europea_fd,
    opcion_americana_bs,
    opcion_americana_bin,
    opcion_americana_mc,
    opcion_americana_fd,
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
    div[class*="block-container"], div[class*="BlockContainer"] { max-width: none !important; }
</style>
""", unsafe_allow_html=True)

st.title(_("mod.title"))

with st.expander(f"📖 {_('mod.how_to_use')}", expanded=False):
    st.markdown(f"""
    1. {_("mod.help_1")}
    2. {_("mod.help_2")}
    3. {_("mod.help_3")}
    4. {_("mod.help_4")}
    5. {_("mod.help_5")}
    6. {_("mod.help_6")}
    """)
st.info(
    "📚 Acá se **comparan modelos** (BS, binomial, Monte Carlo, diferencias finitas, BAW…): "
    "precio en un punto y curvas de sensibilidad. "
    "Para valuación educativa simple (solo BS/BAW) usá **Propiedades de opciones** o **Payoffs y Estrategias** "
    "y los notebooks en `Notebooks/ejes/02_propiedades_opciones_vanilla/`."
)

for k, v in {"mod_result": None, "mod_tabla_comp": None, "mod_punto_meta": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.subheader(_("prop.params"))

row1 = st.columns(4)
with row1[0]:
    S = st.number_input(_("prop.s_spot"), value=100.0, min_value=0.1, step=1.0, key="mod_S")
with row1[1]:
    K = st.number_input(_("prop.k_strike"), value=100.0, min_value=0.1, step=1.0, key="mod_K")
with row1[2]:
    T = st.number_input(_("prop.t_years"), value=1.0, min_value=0.01, step=0.1, key="mod_T")
with row1[3]:
    r = st.number_input(_("prop.r_rate"), value=0.05, min_value=0.0, max_value=1.0, format="%.3f", key="mod_r")

row2 = st.columns(4)
with row2[0]:
    sigma = st.number_input(_("prop.sigma_vol"), value=0.25, min_value=0.01, max_value=2.0, format="%.3f", key="mod_sig")
with row2[1]:
    div = st.number_input(_("prop.div_dividends"), value=0.0, min_value=0.0, max_value=1.0, format="%.3f", key="mod_div")

# ── Precio puntual: comparar todos los modelos ────────────────────────────────
st.divider()
st.subheader(_("mod.point_compare"))
st.caption(_("mod.point_help"))

_MODELS_EUR = ["Black-Scholes", "Binomial", "Monte Carlo", "Diferencias finitas"]
_MODELS_AME = ["Barone-Adesi-Whaley (BAW)", "Binomial", "Monte Carlo (LSM)", "Diferencias finitas"]
_NEEDS_STEPS = {"Binomial", "Monte Carlo", "Diferencias finitas", "Monte Carlo (LSM)"}

pt1, pt2, pt3, pt4 = st.columns([2, 2, 1, 2])
with pt1:
    _ej_opts_pt = {"Europeo": "me.european", "Americano": "me.american"}
    ejercicio_pt = st.radio(
        _("me.exercise"), options=["Europeo", "Americano"],
        format_func=lambda x: _(_ej_opts_pt[x]), horizontal=True, key="mod_ej_pt",
    )
with pt2:
    tipo_pt = st.radio(_("me.type"), ["C", "P"], horizontal=True, key="mod_tipo_pt",
                       format_func=lambda x: "Call" if x == "C" else "Put")
with pt3:
    pasos_pt = st.number_input(_("prop.steps"), value=500, min_value=10, step=100, key="mod_pasos_pt")
with pt4:
    st.write("")
    comp_pt = st.button(_("mod.compare_all"), type="primary", use_container_width=True, key="mod_comp_pt")

_PRICERS_EUR_PT = {
    "Black-Scholes": lambda tp, s, k, t, rv, sig, dv, ps: opcion_europea_bs(tp, s, k, t, rv, sig, dv),
    "Binomial": lambda tp, s, k, t, rv, sig, dv, ps: opcion_europea_bin(tp, s, k, t, rv, sig, dv, int(ps)),
    "Monte Carlo": lambda tp, s, k, t, rv, sig, dv, ps: opcion_europea_mc(tp, s, k, t, rv, sig, dv, int(ps)),
    "Diferencias finitas": lambda tp, s, k, t, rv, sig, dv, ps: opcion_europea_fd(
        tp, s, k, t, rv, sig, dv, M=max(50, min(300, int(ps)))
    ),
}
_PRICERS_AME_PT = {
    "Barone-Adesi-Whaley (BAW)": lambda tp, s, k, t, rv, sig, dv, ps: opcion_americana_bs(tp, s, k, t, rv, sig, dv),
    "Binomial": lambda tp, s, k, t, rv, sig, dv, ps: opcion_americana_bin(tp, s, k, t, rv, sig, dv, int(ps)),
    "Monte Carlo (LSM)": lambda tp, s, k, t, rv, sig, dv, ps: opcion_americana_mc(tp, s, k, t, rv, sig, dv, int(ps)),
    "Diferencias finitas": lambda tp, s, k, t, rv, sig, dv, ps: opcion_americana_fd(
        tp, s, k, t, rv, sig, dv, M=max(50, min(300, int(ps)))
    ),
}


def _precio_punto(modelo, tipo, pasos):
    table = _PRICERS_EUR_PT if ejercicio_pt == "Europeo" else _PRICERS_AME_PT
    try:
        return float(table[modelo](tipo, S, K, T, r, sigma, div, pasos))
    except Exception as exc:
        return str(exc)


if comp_pt:
    modelos_pt = _MODELS_EUR if ejercicio_pt == "Europeo" else _MODELS_AME
    rows_pt = []
    with st.spinner(_("mod.calculating_all")):
        for m in modelos_pt:
            ps = int(pasos_pt) if m in _NEEDS_STEPS else 500
            t0 = time.perf_counter()
            precio = _precio_punto(m, tipo_pt, ps)
            ms = (time.perf_counter() - t0) * 1000.0
            rows_pt.append({"Modelo": m, "Precio": precio, "Tiempo_ms": ms})
    st.session_state.mod_tabla_comp = rows_pt
    st.session_state.mod_punto_meta = {
        "ejercicio": ejercicio_pt,
        "tipo": tipo_pt,
        "S": S, "K": K, "T": T, "r": r, "sigma": sigma, "div": div,
        "pasos": int(pasos_pt),
    }

if st.session_state.mod_tabla_comp is not None:
    meta = st.session_state.mod_punto_meta or {}
    ej_u = meta.get("ejercicio", ejercicio_pt)
    tp_u = meta.get("tipo", tipo_pt)
    tipo_label = "Call" if tp_u == "C" else "Put"
    _ej_disp = _("me.european") if ej_u == "Europeo" else _("me.american")
    st.markdown(
        f"**{_('mod.compare_title', exercise=_ej_disp, type=tipo_label)}**  "
        f"(S={meta.get('S', S)}, K={meta.get('K', K)}, T={meta.get('T', T)}, "
        f"r={meta.get('r', r)}, σ={meta.get('sigma', sigma)}, div={meta.get('div', div)}, "
        f"pasos={meta.get('pasos', pasos_pt)})"
    )
    _col_model = _("me.model")
    _col_price = _("me.price")
    _col_time = _("mod.time_ms")
    comp_rows = []
    for row in st.session_state.mod_tabla_comp:
        p = row.get("Precio")
        t_ms = row.get("Tiempo_ms")
        out = {
            _col_model: row.get("Modelo"),
            _col_price: f"{p:.4f}" if isinstance(p, float) else f"⚠ {p}",
        }
        if isinstance(t_ms, (int, float)):
            out[_col_time] = f"{t_ms:.2f}"
        else:
            out[_col_time] = "—"
        comp_rows.append(out)
    st.dataframe(comp_rows, use_container_width=True, hide_index=True)
    st.caption(_("mod.time_caption"))

st.divider()
st.subheader(_("mod.curves_compare"))

_CURVAS_OPTS = []
_EJ_SHORT = {"Europeo": "Eur", "Americano": "Ame"}
_TP_SHORT = {"C": "Call", "P": "Put"}
for ej in ["Europeo", "Americano"]:
    mods = _MODELS_EUR if ej == "Europeo" else _MODELS_AME
    for mod in mods:
        for tp in ["C", "P"]:
            lbl = f"{_EJ_SHORT[ej]} · {mod} · {_TP_SHORT[tp]}"
            _CURVAS_OPTS.append((lbl, ej, mod, tp))

_curvas_labels = [c[0] for c in _CURVAS_OPTS]
_default_curvas = ["Eur · Black-Scholes · Call", "Ame · Barone-Adesi-Whaley (BAW) · Call"]
_default_curvas = [d for d in _default_curvas if d in _curvas_labels]

col_curv, col_pasos = st.columns([3, 1])
with col_curv:
    curvas_sel = st.multiselect(
        _("mod.curves_select"),
        _curvas_labels,
        default=_default_curvas,
        help=_("mod.curves_help"),
    )
with col_pasos:
    _modelos_en_curvas = set()
    for lbl in curvas_sel:
        idx = _curvas_labels.index(lbl) if lbl in _curvas_labels else -1
        if idx >= 0:
            _modelos_en_curvas.add(_CURVAS_OPTS[idx][2])
    necesita_pasos = any(m in _NEEDS_STEPS for m in _modelos_en_curvas)
    if necesita_pasos:
        pasos = st.number_input(_("prop.steps"), value=100, min_value=10, step=100, key="mod_pasos")
    else:
        pasos = 500
        st.caption(_("prop.steps_na"))

if not curvas_sel:
    st.warning(_("mod.select_curve"))
    st.stop()

st.subheader(_("prop.sensitivity"))

_param_opts = {
    "S": "prop.param_spot",
    "K": "prop.param_strike",
    "T": "prop.param_ttm",
    "r": "prop.param_rate",
    "sigma": "prop.param_vol",
    "div": "prop.param_div",
}
_defaults = {
    "S": (max(1.0, K * 0.5), K * 1.5),
    "K": (max(1.0, S * 0.5), S * 1.5),
    "T": (0.1, 2.0),
    "r": (0.0, 0.20),
    "sigma": (0.05, 0.80),
    "div": (0.0, 0.10),
}

col_ps, col_desde, col_a, col_n = st.columns([2, 1, 1, 1])
with col_ps:
    param_key = st.selectbox(
        _("prop.param_vary"), options=list(_param_opts.keys()),
        format_func=lambda k: _(_param_opts[k]), key="mod_param",
    )
with col_desde:
    dmin, dmax = _defaults[param_key]
    p_desde = st.number_input(
        _("prop.from"), value=round(dmin, 3), min_value=0.0, step=0.1,
        format="%.3f", key=f"mod_desde_{param_key}",
    )
with col_a:
    p_a = st.number_input(
        _("prop.to"), value=round(dmax, 3), min_value=0.0, step=0.1,
        format="%.3f", key=f"mod_a_{param_key}",
    )
with col_n:
    n_pts = st.number_input(_("prop.points"), value=20, min_value=5, max_value=20, step=5, key="mod_npts")

if p_desde >= p_a:
    st.error(_("prop.from_to_error"))
    st.stop()

marcar_base = st.checkbox(_("prop.mark_base"), value=True, key="mod_mark")
calcular = st.button(_("prop.calculate"), type="primary", use_container_width=True, key="mod_calc")

_PRICERS_EUR = {
    "Black-Scholes": lambda tp, s, k, t, rv, sig, dv: opcion_europea_bs(tp, s, k, t, rv, sig, dv),
    "Binomial": lambda tp, s, k, t, rv, sig, dv: opcion_europea_bin(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Monte Carlo": lambda tp, s, k, t, rv, sig, dv: opcion_europea_mc(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Diferencias finitas": lambda tp, s, k, t, rv, sig, dv: opcion_europea_fd(
        tp, s, k, t, rv, sig, dv, M=max(50, min(300, int(pasos)))
    ),
}
_PRICERS_AME = {
    "Barone-Adesi-Whaley (BAW)": lambda tp, s, k, t, rv, sig, dv: opcion_americana_bs(tp, s, k, t, rv, sig, dv),
    "Binomial": lambda tp, s, k, t, rv, sig, dv: opcion_americana_bin(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Monte Carlo (LSM)": lambda tp, s, k, t, rv, sig, dv: opcion_americana_mc(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Diferencias finitas": lambda tp, s, k, t, rv, sig, dv: opcion_americana_fd(
        tp, s, k, t, rv, sig, dv, M=max(50, min(300, int(pasos)))
    ),
}


def _get_pricer(ejercicio, modelo):
    return _PRICERS_EUR[modelo] if ejercicio == "Europeo" else _PRICERS_AME[modelo]


def _clamp(val, key):
    if key in ("sigma", "T") and val <= 0:
        return 1e-4
    if key in ("S", "K") and val <= 0:
        return 0.01
    return val


def _precio_base(ej, modelo, tipo):
    try:
        return _get_pricer(ej, modelo)(tipo, S, K, T, r, sigma, div)
    except Exception:
        return np.nan


def _calcular_curva(ej, modelo, tipo, x_vals):
    base = {"S": S, "K": K, "T": T, "r": r, "sigma": sigma, "div": div}
    pricer = _get_pricer(ej, modelo)
    precios = []
    for x in x_vals:
        base[param_key] = _clamp(x, param_key)
        try:
            p = pricer(tipo, base["S"], base["K"], base["T"], base["r"], base["sigma"], base["div"])
            precios.append(float(p))
        except Exception:
            precios.append(np.nan)
    return np.array(precios)


if calcular:
    x_vals = np.linspace(p_desde, p_a, max(5, min(20, int(n_pts))))
    results = {}
    base_pts = {}
    with st.spinner(_("prop.calculating")):
        for lbl in curvas_sel:
            idx = _curvas_labels.index(lbl) if lbl in _curvas_labels else -1
            if idx < 0:
                continue
            _u, ej, mod, tp = _CURVAS_OPTS[idx]
            results[lbl] = _calcular_curva(ej, mod, tp, x_vals)
            if marcar_base:
                base_pts[lbl] = _precio_base(ej, mod, tp)
    base_param_val = {"S": S, "K": K, "T": T, "r": r, "sigma": sigma, "div": div}[param_key]
    st.session_state.mod_result = {
        "x_vals": x_vals,
        "results": results,
        "base_pts": base_pts,
        "base_param_val": base_param_val,
        "param_key": param_key,
        "marcar_base": marcar_base,
        "curvas_sel": curvas_sel,
    }

res = st.session_state.mod_result
if res is None:
    st.info(_("mod.configure_info"))
    st.stop()

x_vals = res["x_vals"]
results = res["results"]
base_pts = res["base_pts"]
base_param_val = res["base_param_val"]
_param_key = res["param_key"]
_param_sel = _(_param_opts[_param_key])
_marcar_base = res["marcar_base"]
_curvas_sel = res["curvas_sel"]
_COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]

fig, ax = plt.subplots(figsize=(11, 5), dpi=110)
for i, lbl in enumerate(_curvas_sel):
    if lbl not in results:
        continue
    curva = results[lbl]
    valid = np.isfinite(curva)
    if not np.any(valid):
        continue
    color = _COLORS[i % len(_COLORS)]
    ax.plot(x_vals[valid], curva[valid], color=color, linewidth=2.0, label=lbl)
    if _marcar_base and lbl in base_pts and np.isfinite(base_pts[lbl]):
        if p_desde <= base_param_val <= p_a:
            pb = base_pts[lbl]
            ax.scatter([base_param_val], [pb], color=color, zorder=5, s=80,
                       marker="o", edgecolors="white", linewidths=1.2)
            ax.annotate(f" {pb:.3f}", xy=(base_param_val, pb), xytext=(6, 0),
                        textcoords="offset points", fontsize=8, color=color, va="center")

if _marcar_base and p_desde <= base_param_val <= p_a:
    ax.axvline(base_param_val, color="gray", linestyle=":", linewidth=1.2,
               label=f"{_param_sel} base = {base_param_val:.3f}")

ax.legend(fontsize=8, loc="best")
ax.set_xlabel(_param_sel, fontsize=11)
ax.set_ylabel(_("prop.option_price"), fontsize=11)
ax.set_title(_("mod.sensitivity_title", param=_param_sel), fontsize=12)
ax.grid(True, alpha=0.25)
plt.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)

rows = {_param_sel: x_vals}
for lbl in _curvas_sel:
    if lbl in results:
        rows[lbl] = results[lbl]
import pandas as _pd_export
df_exp = _pd_export.DataFrame(rows)
buf = io.BytesIO()
df_exp.to_excel(buf, index=False, sheet_name=_("mod.sheet_name"), engine="openpyxl")
buf.seek(0)
st.download_button(
    f"📥 {_('prop.export_excel')}", data=buf,
    file_name=f"modelos_pricing_{_param_key}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="mod_export",
)
