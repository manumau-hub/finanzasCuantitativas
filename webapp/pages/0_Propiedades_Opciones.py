# -*- coding: utf-8 -*-
"""
Propiedades de opciones — Sensibilidad del precio ante variación de parámetros.

Solo opciones europeas vanilla. Se fijan todos los parámetros excepto uno,
que se barre en un intervalo para ver cómo responde el precio.
"""
import io
import sys
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

st.title(_("prop.title"))

with st.expander(f"📖 {_('prop.how_to_use')}", expanded=False):
    st.markdown(f"""
    1. {_("prop.help_1")}
    2. {_("prop.help_2")}
    3. {_("prop.help_3")}
    4. {_("prop.help_4")}
    5. {_("prop.help_5")}
    6. {_("prop.help_6")}
    """)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {"prop_result": None, "prop_params": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════════════════════
# PARÁMETROS — 2 filas
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("prop.params"))

row1 = st.columns(4)
with row1[0]:
    S = st.number_input(_("prop.s_spot"), value=100.0, min_value=0.1, step=1.0)
with row1[1]:
    K = st.number_input(_("prop.k_strike"), value=100.0, min_value=0.1, step=1.0)
with row1[2]:
    T = st.number_input(_("prop.t_years"), value=1.0, min_value=0.01, step=0.1)
with row1[3]:
    r = st.number_input(_("prop.r_rate"), value=0.05, min_value=0.0, max_value=1.0, format="%.3f")

row2 = st.columns(4)
with row2[0]:
    sigma = st.number_input(_("prop.sigma_vol"), value=0.25, min_value=0.01, max_value=2.0, format="%.3f")
with row2[1]:
    div = st.number_input(_("prop.div_dividends"), value=0.0, min_value=0.0, max_value=1.0, format="%.3f")

# ════════════════════════════════════════════════════════════════════════════
# CURVAS A COMPARAR (ejercicio + modelo + tipo)
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("prop.curves_compare") if _("prop.curves_compare") != "prop.curves_compare" else "Curvas a comparar")

_MODELS_EUR = ["Black-Scholes", "Binomial", "Monte Carlo", "Diferencias finitas"]
_MODELS_AME = ["Barone-Adesi-Whaley (BAW)", "Binomial", "Monte Carlo (LSM)", "Diferencias finitas"]
_NEEDS_STEPS = {"Binomial", "Monte Carlo", "Diferencias finitas", "Monte Carlo (LSM)"}

# Construir lista de opciones: "Eur · BS · Call", "Ame · BAW · Put", etc.
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
if not _default_curvas:
    _default_curvas = [_curvas_labels[0], _curvas_labels[16]]  # Eur BS Call, Ame BAW Call

col_curv, col_pasos = st.columns([3, 1])
with col_curv:
    curvas_sel = st.multiselect(
        _("prop.curves_select") if _("prop.curves_select") != "prop.curves_select" else "Seleccionar curvas",
        _curvas_labels,
        default=_default_curvas,
        help=_("prop.curves_help") if _("prop.curves_help") != "prop.curves_help" else "Elegí una o más curvas para comparar en el mismo gráfico.",
    )
with col_pasos:
    _modelos_en_curvas = set()
    for lbl in curvas_sel:
        idx = _curvas_labels.index(lbl) if lbl in _curvas_labels else -1
        if idx >= 0:
            _modelos_en_curvas.add(_CURVAS_OPTS[idx][2])
    necesita_pasos = any(m in _NEEDS_STEPS for m in _modelos_en_curvas)
    if necesita_pasos:
        pasos = st.number_input(_("prop.steps"), value=100, min_value=10, step=100)
    else:
        pasos = 500
        st.caption(_("prop.steps_na"))

if not curvas_sel:
    st.warning(_("prop.select_model"))
    st.stop()

# Resolver curvas seleccionadas a (ejercicio, modelo, tipo)
curvas_resueltas = []
for lbl in curvas_sel:
    idx = _curvas_labels.index(lbl) if lbl in _curvas_labels else -1
    if idx >= 0:
        _unused, ej, mod, tp = _CURVAS_OPTS[idx]
        curvas_resueltas.append((ej, mod, tp))

# ════════════════════════════════════════════════════════════════════════════
# SENSIBILIDAD
# ════════════════════════════════════════════════════════════════════════════
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
    "S":     (max(1.0, K * 0.5),     K * 1.5),
    "K":     (max(1.0, S * 0.5),     S * 1.5),
    "T":     (0.1, 2.0),
    "r":     (0.0, 0.20),
    "sigma": (0.05, 0.80),
    "div":   (0.0, 0.10),
}

col_ps, col_desde, col_a, col_n = st.columns([2, 1, 1, 1])
with col_ps:
    param_key = st.selectbox(_("prop.param_vary"), options=list(_param_opts.keys()),
                             format_func=lambda k: _(_param_opts[k]))
with col_desde:
    dmin, dmax = _defaults[param_key]
    p_desde = st.number_input(
        _("prop.from"), value=round(dmin, 3), min_value=0.0, step=0.1,
        format="%.3f", key=f"prop_desde_{param_key}",
    )
with col_a:
    p_a = st.number_input(
        _("prop.to"), value=round(dmax, 3), min_value=0.0, step=0.1,
        format="%.3f", key=f"prop_a_{param_key}",
    )
with col_n:
    n_pts = st.number_input(_("prop.points"), value=20, min_value=5, max_value=20, step=5)

if p_desde >= p_a:
    st.error(_("prop.from_to_error"))
    st.stop()

# Opciones
marcar_base = st.checkbox(_("prop.mark_base"), value=True)

# ── Botón Calcular ────────────────────────────────────────────────────────────
calcular = st.button(_("prop.calculate"), type="primary", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# CÁLCULO
# ════════════════════════════════════════════════════════════════════════════
_PRICERS_EUR = {
    "Black-Scholes":       lambda tp, s, k, t, rv, sig, dv: opcion_europea_bs(tp, s, k, t, rv, sig, dv),
    "Binomial":            lambda tp, s, k, t, rv, sig, dv: opcion_europea_bin(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Monte Carlo":         lambda tp, s, k, t, rv, sig, dv: opcion_europea_mc(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Diferencias finitas": lambda tp, s, k, t, rv, sig, dv: opcion_europea_fd(tp, s, k, t, rv, sig, dv, M=max(50, min(300, int(pasos)))),
}
_PRICERS_AME = {
    "Barone-Adesi-Whaley (BAW)": lambda tp, s, k, t, rv, sig, dv: opcion_americana_bs(tp, s, k, t, rv, sig, dv),
    "Binomial":                  lambda tp, s, k, t, rv, sig, dv: opcion_americana_bin(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Monte Carlo (LSM)":         lambda tp, s, k, t, rv, sig, dv: opcion_americana_mc(tp, s, k, t, rv, sig, dv, int(pasos)),
    "Diferencias finitas":       lambda tp, s, k, t, rv, sig, dv: opcion_americana_fd(tp, s, k, t, rv, sig, dv, M=max(50, min(300, int(pasos)))),
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
    results = {}  # {label: array}
    base_pts = {}  # {label: precio_base}

    with st.spinner(_("prop.calculating")):
        for lbl in curvas_sel:
            idx = _curvas_labels.index(lbl) if lbl in _curvas_labels else -1
            if idx < 0:
                continue
            _unused, ej, mod, tp = _CURVAS_OPTS[idx]
            results[lbl] = _calcular_curva(ej, mod, tp, x_vals)
            if marcar_base:
                base_pts[lbl] = _precio_base(ej, mod, tp)

    base_param_val = {"S": S, "K": K, "T": T, "r": r, "sigma": sigma, "div": div}[param_key]

    st.session_state.prop_result = {
        "x_vals": x_vals,
        "results": results,
        "base_pts": base_pts,
        "base_param_val": base_param_val,
        "param_key": param_key,
        "marcar_base": marcar_base,
        "curvas_sel": curvas_sel,
    }

# ════════════════════════════════════════════════════════════════════════════
# GRÁFICO (persiste en session state)
# ════════════════════════════════════════════════════════════════════════════
res = st.session_state.prop_result
if res is None:
    st.info(_("prop.configure_info"))
    st.stop()

x_vals         = res["x_vals"]
results        = res["results"]
base_pts       = res["base_pts"]
base_param_val = res["base_param_val"]
_param_key     = res["param_key"]
_param_sel     = _(_param_opts[_param_key])
_marcar_base   = res["marcar_base"]
_curvas_sel    = res["curvas_sel"]

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
    ax.plot(x_vals[valid], curva[valid], color=color, linestyle="-",
            linewidth=2.0, label=lbl)

    if _marcar_base and lbl in base_pts:
        pb = base_pts[lbl]
        if np.isfinite(pb) and p_desde <= base_param_val <= p_a:
            ax.scatter([base_param_val], [pb], color=color, zorder=5,
                       s=80, marker="o", edgecolors="white", linewidths=1.2)
            ax.annotate(
                f" {pb:.3f}",
                xy=(base_param_val, pb),
                xytext=(6, 0), textcoords="offset points",
                fontsize=8, color=color, va="center",
            )

if _marcar_base and p_desde <= base_param_val <= p_a:
    ax.axvline(base_param_val, color="gray", linestyle=":", linewidth=1.2,
               label=f"{_param_sel} base = {base_param_val:.3f}")

ax.legend(fontsize=8, loc="best")
ax.set_xlabel(_param_sel, fontsize=11)
ax.set_ylabel(_("prop.option_price"), fontsize=11)
titulo = _("prop.sensitivity_title", param=_param_sel, exercise="")
if titulo.endswith(" []"):
    titulo = titulo[:-3]
titulo = titulo or f"Sensibilidad del precio — {_param_sel}"
ax.set_title(titulo, fontsize=12)
ax.grid(True, alpha=0.25)
ax.autoscale_view()
plt.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ── Exportar ─────────────────────────────────────────────────────────────────
rows = {_param_sel: x_vals}
for lbl in _curvas_sel:
    if lbl in results:
        rows[lbl] = results[lbl]

import pandas as _pd_export  # lazy import — solo para exportar Excel
df_exp = _pd_export.DataFrame(rows)
buf = io.BytesIO()
df_exp.to_excel(buf, index=False, sheet_name=_("prop.sheet_sensitivity"), engine="openpyxl")
buf.seek(0)
fn = f"propiedades_{_param_key}_curvas.xlsx"
st.download_button(
    f"📥 {_('prop.export_excel')}", data=buf, file_name=fn,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="prop_export",
)
