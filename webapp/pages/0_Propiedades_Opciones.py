# -*- coding: utf-8 -*-
"""
Propiedades de opciones — Sensibilidad del precio ante variación de parámetros.

Sin menú de modelos: europea → Black-Scholes; americana → BAW.
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
from Codigo.pricing import opcion_europea_bs, opcion_americana_bs

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
    div[class*="block-container"], div[class*="BlockContainer"] { max-width: none !important; }
</style>
""", unsafe_allow_html=True)

st.title(_("prop.title"))

with st.expander(f"📖 {_('prop.how_to_use')}", expanded=False):
    st.markdown(f"""
    1. {_("prop.help_1_simple")}
    2. {_("prop.help_2_simple")}
    3. {_("prop.help_3_simple")}
    4. {_("prop.help_4_simple")}
    5. {_("prop.help_5_simple")}
    """)
st.info(
    "📚 **Teoría (Eje 2):** `Notebooks/ejes/02_propiedades_opciones_vanilla/` — "
    "**02a_sensibilidades_parametros** y **02b_paridad_intrinseco_moneyness**. "
    "La comparación entre modelos numéricos está en **Modelos de Pricing**."
)

for k, v in {"prop_result": None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
with row2[2]:
    tipo = st.radio(_("prop.base_type"), ["C", "P"], horizontal=True,
                    format_func=lambda x: "Call" if x == "C" else "Put")
with row2[3]:
    ejercicio = st.radio(
        _("prop.exercise"),
        ["Europeo", "Americano"],
        horizontal=True,
        format_func=lambda x: _("prop.european") if x == "Europeo" else _("prop.american"),
    )

modelo_label = "Black-Scholes" if ejercicio == "Europeo" else "Barone-Adesi-Whaley (BAW)"
pricer = opcion_europea_bs if ejercicio == "Europeo" else opcion_americana_bs
st.caption(f"Motor de precio: **{modelo_label}** (fijo según el ejercicio).")

overlay = st.checkbox(_("prop.overlay_call_put"), value=False)
marcar_base = st.checkbox(_("prop.mark_base"), value=True)

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
        _("prop.param_vary"),
        options=list(_param_opts.keys()),
        format_func=lambda k: _(_param_opts[k]),
    )
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

calcular = st.button(_("prop.calculate"), type="primary", use_container_width=True)


def _clamp(val, key):
    if key in ("sigma", "T") and val <= 0:
        return 1e-4
    if key in ("S", "K") and val <= 0:
        return 0.01
    return val


def _precio(tp, s, k, t, rv, sig, dv):
    try:
        return float(pricer(tp, s, k, t, rv, sig, dv))
    except Exception:
        return np.nan


def _curva(tp, x_vals):
    base = {"S": S, "K": K, "T": T, "r": r, "sigma": sigma, "div": div}
    out = []
    for x in x_vals:
        base[param_key] = _clamp(x, param_key)
        out.append(_precio(tp, base["S"], base["K"], base["T"], base["r"], base["sigma"], base["div"]))
    return np.array(out)


if calcular:
    x_vals = np.linspace(p_desde, p_a, max(5, min(20, int(n_pts))))
    tipos = ["C", "P"] if overlay else [tipo]
    results = {}
    base_pts = {}
    with st.spinner(_("prop.calculating")):
        for tp in tipos:
            lbl = f"{'Call' if tp == 'C' else 'Put'} · {modelo_label}"
            results[lbl] = _curva(tp, x_vals)
            if marcar_base:
                base_pts[lbl] = _precio(tp, S, K, T, r, sigma, div)
    base_param_val = {"S": S, "K": K, "T": T, "r": r, "sigma": sigma, "div": div}[param_key]
    st.session_state.prop_result = {
        "x_vals": x_vals,
        "results": results,
        "base_pts": base_pts,
        "base_param_val": base_param_val,
        "param_key": param_key,
        "marcar_base": marcar_base,
        "ejercicio": ejercicio,
        "modelo_label": modelo_label,
    }

res = st.session_state.prop_result
if res is None:
    st.info(_("prop.configure_info"))
    st.stop()

x_vals = res["x_vals"]
results = res["results"]
base_pts = res["base_pts"]
base_param_val = res["base_param_val"]
_param_key = res["param_key"]
_param_sel = _(_param_opts[_param_key])
_marcar_base = res["marcar_base"]
_COLORS = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"]

fig, ax = plt.subplots(figsize=(11, 5), dpi=110)
for i, (lbl, curva) in enumerate(results.items()):
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

ax.legend(fontsize=9, loc="best")
ax.set_xlabel(_param_sel, fontsize=11)
ax.set_ylabel(_("prop.option_price"), fontsize=11)
ax.set_title(
    _("prop.sensitivity_title", param=_param_sel, exercise=res.get("ejercicio", "")),
    fontsize=12,
)
ax.grid(True, alpha=0.25)
plt.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)

rows = {_param_sel: x_vals}
rows.update(results)
import pandas as _pd_export
df_exp = _pd_export.DataFrame(rows)
buf = io.BytesIO()
df_exp.to_excel(buf, index=False, sheet_name=_("prop.sheet_sensitivity"), engine="openpyxl")
buf.seek(0)
st.download_button(
    f"📥 {_('prop.export_excel')}", data=buf,
    file_name=f"propiedades_{_param_key}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="prop_export",
)
