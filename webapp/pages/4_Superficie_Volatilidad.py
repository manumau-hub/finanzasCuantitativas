# -*- coding: utf-8 -*-
"""
Superficie de volatilidad implícita — IV vs Delta × TTM.

3 pasos independientes con session state:
  1. Obtener información de mercado  → Raw IV
  2. Calcular superficie             → tabla suavizada
  3. Graficar superficie 3D          → plotly interactivo
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from pathlib import Path
_webapp = Path(__file__).resolve().parent.parent
if str(_webapp) not in sys.path:
    sys.path.insert(0, str(_webapp))

import streamlit as st

from i18n import _, render_language_selector

st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }
</style>
""", unsafe_allow_html=True)

render_language_selector()

st.title(_("vol.title"))

# ── Imports ──────────────────────────────────────────────────────────────────
try:
    from Codigo.data.market_data import (
        get_spot, get_expirations, get_options_chain,
        get_dividend_yield, get_risk_free_rate,
    )
    import pandas as pd
    _MARKET_DATA_OK = True
except Exception as e:
    _MARKET_DATA_OK = False
    _MARKET_DATA_ERR = str(e)

if not _MARKET_DATA_OK:
    st.error(_("vol.market_data_error", e=_MARKET_DATA_ERR))
    if "numpy.dtype" in _MARKET_DATA_ERR or "binary incompatibility" in _MARKET_DATA_ERR:
        st.info(_("vol.numpy_fix"))
    st.stop()

script_dir = Path(__file__).resolve().parent.parent
fetch_script = script_dir / "_fetch_vol_surface.py"

# ── Session state ─────────────────────────────────────────────────────────────
_DEFAULTS = {
    "vs_ticker": "",
    "vs_all_exps": [],
    "vs_loaded_exps": [],
    "vs_chain_df": None,
    "vs_raw_df": None,
    "vs_surf_df": None,
    "vs_spot": None,
    "vs_r": None,
    "vs_div": None,
    # Paso 3: persistencia del gráfico
    "vs_plot_tipo": "Calls",
    "vs_plot_color": "RdYlGn_r",
    "vs_show_plot": False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _reset():
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def _run_surface(chain_df, spot, r, div):
    tmpdir = tempfile.mkdtemp(prefix="vol_surface_")
    chain_csv = os.path.join(tmpdir, "chain.csv")
    chain_df.to_csv(chain_csv, index=False)
    result = subprocess.run(
        [sys.executable, str(fetch_script), chain_csv, str(spot), str(r), str(div)],
        capture_output=True, text=True, timeout=120,
        cwd=str(script_dir.parent),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    raw_path  = os.path.join(tmpdir, "raw.csv")
    surf_path = os.path.join(tmpdir, "surf.csv")
    if not os.path.isfile(raw_path) or not os.path.isfile(surf_path):
        raise RuntimeError(f"El engine no generó los archivos de salida.\n{result.stderr}")
    return pd.read_csv(raw_path), pd.read_csv(surf_path)


def _build_plotly_fig(surf_df, tipo_plot, colorscale, ticker):
    import plotly.graph_objects as go
    import plotly.subplots as sp

    def _pivot(cp_val):
        df = surf_df[surf_df["CallPut"] == cp_val].copy()
        df["ImpliedVol"] = pd.to_numeric(df["ImpliedVol"], errors="coerce")
        df = df.dropna(subset=["ImpliedVol", "Delta", "Days"])
        df["Delta"] = df["Delta"].abs()
        pivot = (
            df.pivot_table(index="Days", columns="Delta",
                           values="ImpliedVol", aggfunc="mean")
            .sort_index().sort_index(axis=1)
        )
        if pivot.empty:
            return None, None, None
        return (
            pivot.columns.to_numpy(dtype=float),
            pivot.index.to_numpy(dtype=float),
            pivot.values * 100,
        )

    scene_kw = dict(
        xaxis_title="Delta (%)",
        yaxis_title="TTM (días)",
        zaxis_title="IV (%)",
        camera=dict(eye=dict(x=1.6, y=-1.6, z=0.8)),
    )

    if tipo_plot == "Calls y Puts (lado a lado)":
        fig = sp.make_subplots(
            rows=1, cols=2,
            specs=[[{"type": "surface"}, {"type": "surface"}]],
            subplot_titles=("Calls", "Puts"),
            horizontal_spacing=0.05,
        )
        for col_idx, (cp, label) in enumerate([("C", "Calls"), ("P", "Puts")], start=1):
            x, y, z = _pivot(cp)
            if z is not None:
                fig.add_trace(
                    go.Surface(
                        x=x, y=y, z=z,
                        colorscale=colorscale,
                        showscale=(col_idx == 1),
                        colorbar=dict(title="IV (%)", x=0.44 if col_idx == 1 else 1.0),
                        hovertemplate="Δ: %{x:.0f}%<br>TTM: %{y:.0f}d<br>IV: %{z:.2f}%<extra></extra>",
                        name=label,
                    ),
                    row=1, col=col_idx,
                )
        fig.update_layout(
            title=_("vol.surface_title", ticker=ticker),
            height=600, margin=dict(l=0, r=0, t=50, b=0),
            scene=scene_kw, scene2=scene_kw,
        )
    else:
        cp_val = "C" if tipo_plot == "Calls" else "P"
        x, y, z = _pivot(cp_val)
        if z is None:
            return None
        fig = go.Figure(data=[go.Surface(
            x=x, y=y, z=z,
            colorscale=colorscale,
            colorbar=dict(title="IV (%)"),
            hovertemplate="Δ: %{x:.0f}%<br>TTM: %{y:.0f}d<br>IV: %{z:.2f}%<extra></extra>",
        )])
        fig.update_layout(
            title=_("vol.surface_title_type", ticker=ticker, type=tipo_plot),
            scene=scene_kw,
            height=580, margin=dict(l=0, r=0, t=50, b=0),
        )
    return fig


# ════════════════════════════════════════════════════════════════════════════
# PASO 1 — Obtener información de mercado
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("vol.step1"))

with st.form("form_ticker"):
    c1, c2 = st.columns([2, 1])
    with c1:
        ticker_input = st.text_input(_("vol.ticker"), placeholder=_("vol.ticker_placeholder"), max_chars=10)
    with c2:
        max_exp = st.number_input(_("vol.max_exp"), min_value=1, max_value=30, value=8, step=1)
    submitted = st.form_submit_button(
        _("vol.fetch_market"), type="primary", use_container_width=True
    )

if submitted:
    ticker = ticker_input.strip().upper()
    if not ticker:
        st.warning("Ingresá un ticker válido.")
        st.stop()

    _reset()
    st.session_state.vs_ticker = ticker

    progress = st.progress(0, text="Iniciando...")
    status   = st.empty()
    try:
        progress.progress(5,  text="Obteniendo precio spot...")
        status.caption(f"Obteniendo precio spot de {ticker}...")
        spot = get_spot(ticker)

        progress.progress(15, text="Obteniendo vencimientos...")
        status.caption("Obteniendo vencimientos disponibles...")
        all_exps = get_expirations(ticker) or []
        if not all_exps:
            st.error("No hay vencimientos para este ticker.")
            st.stop()

        st.session_state.vs_all_exps = all_exps
        st.session_state.vs_spot     = spot

        n_load       = min(int(max_exp), len(all_exps))
        exps_to_load = all_exps[:n_load]

        panels = []
        for i, exp in enumerate(exps_to_load):
            pct = 18 + int(50 * (i + 1) / n_load)
            progress.progress(pct, text=f"Cargando chain ({i+1}/{n_load})...")
            status.caption(f"Vencimiento {i+1}/{n_load}: {exp}")
            ch = get_options_chain(ticker, exp)
            if ch is not None and not ch.empty:
                panels.append(ch)

        chain_df = pd.concat(panels, ignore_index=True) if panels else pd.DataFrame()
        if chain_df.empty:
            st.error(_("vol.error_chain"))
            st.stop()

        progress.progress(72, text=_("vol.progress_r_div"))
        status.caption(_("vol.progress_r_div_cap"))
        r   = get_risk_free_rate()
        div = get_dividend_yield(ticker)

        progress.progress(100, text=_("vol.progress_done"))
        status.empty()

        st.session_state.vs_chain_df    = chain_df
        st.session_state.vs_loaded_exps = exps_to_load
        st.session_state.vs_r           = r
        st.session_state.vs_div         = div

    except Exception as e:
        progress.empty(); status.empty()
        st.error(_("vol.error_load", e=str(e)))
        st.stop()

    # Rerun limpio para que el resto de la página se renderice correctamente
    st.rerun()

# ── Detener si no hay datos ───────────────────────────────────────────────────
if st.session_state.vs_chain_df is None:
    st.info(_("vol.enter_to_start"))
    st.stop()

# Variables locales desde session state
ticker      = st.session_state.vs_ticker
spot        = st.session_state.vs_spot
r           = st.session_state.vs_r
div         = st.session_state.vs_div
chain_df    = st.session_state.vs_chain_df
all_exps    = st.session_state.vs_all_exps
loaded_exps = st.session_state.vs_loaded_exps

st.success(_("vol.success_data", ticker=ticker, spot=f"{spot:.2f}", r=f"{r:.2%}", div=f"{div:.2%}",
           contracts=f"{len(chain_df):,}", n_exp=len(loaded_exps)))

# Vencimientos restantes
remaining_exps = [e for e in all_exps if e not in set(loaded_exps)]
if remaining_exps:
    with st.expander(
        f"➕  Quedan **{len(remaining_exps)}** vencimientos sin cargar — click para agregar más",
        expanded=False,
    ):
        st.markdown("**Sin cargar:**  \n" + "  ".join(f"`{e}`" for e in remaining_exps))
        st.caption(f"Ya cargados ({len(loaded_exps)}): {', '.join(loaded_exps)}")
        with st.form("form_mas_exps"):
            n_extra = st.number_input(
                "¿Cuántos adicionales?",
                min_value=1, max_value=len(remaining_exps),
                value=min(5, len(remaining_exps)), step=1,
            )
            add_sub = st.form_submit_button(
                _("vol.add_update"), type="secondary", use_container_width=True
            )
        if add_sub:
            prog2 = st.progress(0, text=_("vol.loading_extra"))
            stat2 = st.empty()
            exps_extra = remaining_exps[:int(n_extra)]
            panels_extra = []
            for i, exp in enumerate(exps_extra):
                pct = int(90 * (i + 1) / len(exps_extra))
                prog2.progress(pct, text=f"Cargando ({i+1}/{len(exps_extra)})...")
                stat2.caption(f"Vencimiento: {exp}")
                ch = get_options_chain(ticker, exp)
                if ch is not None and not ch.empty:
                    panels_extra.append(ch)
            prog2.progress(100, text=_("vol.progress_done")); stat2.empty()
            if panels_extra:
                st.session_state.vs_chain_df    = pd.concat([chain_df] + panels_extra, ignore_index=True)
                st.session_state.vs_loaded_exps = loaded_exps + exps_extra
                st.session_state.vs_surf_df     = None
                st.session_state.vs_show_plot   = False
                st.rerun()
            else:
                st.warning(_("vol.no_extra_loaded"))

with st.expander(_("vol.view_raw"), expanded=False):
    st.dataframe(chain_df, use_container_width=True, hide_index=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# PASO 2 — Calcular superficie de volatilidad
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("vol.step2"))

if st.button(_("vol.calc_surface"), type="primary", use_container_width=True):
    progress = st.progress(0, text=_("vol.progress_calc"))
    status   = st.empty()
    try:
        progress.progress(10, text="Preparando datos...")
        status.caption("Preparando datos para el engine de volatilidad...")

        progress.progress(20, text="Ejecutando gaussian_smooth (subproceso)...")
        status.caption("Suavizado Vega-weighted — puede tardar unos segundos...")

        raw_df, surf_df = _run_surface(chain_df, spot, r, div)

        progress.progress(95, text="Leyendo resultados...")
        status.caption("Cargando resultados...")
        progress.progress(100, text="¡Listo!")
        status.empty()

        st.session_state.vs_raw_df    = raw_df
        st.session_state.vs_surf_df   = surf_df
        st.session_state.vs_show_plot = False   # resetear plot al recalcular

    except subprocess.TimeoutExpired:
        progress.empty(); status.empty()
        st.error(_("vol.timeout"))
        st.stop()
    except Exception as e:
        progress.empty(); status.empty()
        st.error(_("vol.calc_error", e=str(e)))
        st.stop()

    # Rerun limpio para que Paso 3 aparezca correctamente
    st.rerun()

if st.session_state.vs_surf_df is None:
    st.info(_("vol.press_calc"))
    st.stop()

raw_df  = st.session_state.vs_raw_df
surf_df = st.session_state.vs_surf_df

st.success(
    f"Superficie calculada: {len(surf_df)} puntos | "
    f"Raw IV: {len(raw_df)} observaciones válidas"
)

tab_surf, tab_raw = st.tabs(["Superficie suavizada", "Raw IV procesado"])
with tab_surf:
    st.dataframe(surf_df, use_container_width=True, hide_index=True)
with tab_raw:
    st.dataframe(raw_df, use_container_width=True, hide_index=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# PASO 3 — Graficar superficie 3D
# ════════════════════════════════════════════════════════════════════════════
st.subheader(_("vol.step3"))

_OPT_TYPES_VAL = ["Calls", "Puts", "Calls y Puts (lado a lado)"]
c1, c2 = st.columns(2)
with c1:
    tipo_plot = st.selectbox(
        _("vol.opt_type"),
        _OPT_TYPES_VAL,
        index=_OPT_TYPES_VAL.index(st.session_state.vs_plot_tipo) if st.session_state.vs_plot_tipo in _OPT_TYPES_VAL else 0,
        key="sel_tipo",
        format_func=lambda x: _("vol.calls") if x == "Calls" else (_("vol.puts") if x == "Puts" else _("vol.calls_puts")),
    )
with c2:
    colorscale = st.selectbox(
        _("vol.color_scale"),
        ["RdYlGn_r", "Viridis", "Plasma", "Hot_r", "Bluered"],
        index=["RdYlGn_r", "Viridis", "Plasma", "Hot_r", "Bluered"].index(
            st.session_state.vs_plot_color
        ),
        key="sel_color",
    )

# Guardar selección en session state
st.session_state.vs_plot_tipo  = tipo_plot
st.session_state.vs_plot_color = colorscale

if st.button(_("vol.plot_surface"), type="primary", use_container_width=True):
    st.session_state.vs_show_plot = True

# Mostrar gráfico si está activo (persiste al cambiar selectboxes)
if st.session_state.vs_show_plot:
    with st.spinner(_("vol.building")):
        fig = _build_plotly_fig(
            surf_df,
            st.session_state.vs_plot_tipo,
            st.session_state.vs_plot_color,
            ticker,
        )
    if fig is None:
        st.warning(_("vol.no_data_plot"))
    else:
        st.plotly_chart(fig, use_container_width=True)
