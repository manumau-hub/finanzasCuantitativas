# -*- coding: utf-8 -*-
"""Notebooks - JupyterLab + índice de ejes del curso."""
import socket
import subprocess
import sys
from pathlib import Path

_webapp = Path(__file__).resolve().parent.parent
if str(_webapp) not in sys.path:
    sys.path.insert(0, str(_webapp))

import streamlit as st

_EJES = [
    ("1 · Introducción", "Notebooks/ejes/01_introduccion_derivados/", "01a fundamentos · 01b forwards/opciones · 01c payoffs/PnL · 01d paneles"),
    ("2 · Propiedades vanilla", "Notebooks/ejes/02_propiedades_opciones_vanilla/", "02a sensibilidades · 02b paridad / intrínseco / moneyness"),
    ("3 · Estrategias", "Notebooks/ejes/03_estrategias/", "03a spreads y butterflies · 03b volatilidad y coberturas"),
    ("4 · Market data", "Notebooks/ejes/04_market_data_i/", "04a US spot/cadena · 04b IV · 04c BYMA paneles"),
]


def _is_port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False


def _find_jupyter_port() -> int | None:
    for port in (8888, 8889, 8890):
        if _is_port_in_use(port):
            return port
    return None


def _launch_jupyter_in_new_terminal():
    config_path = Path(__file__).resolve().parent.parent / "jupyter_server_config.py"
    root = Path(__file__).resolve().parent.parent.parent
    try:
        if sys.platform == "win32":
            bat = root / "_launch_jupyter.bat"
            bat.write_text(
                f'@echo off\ncd /d "{root}"\npython -m jupyterlab --config="{config_path}"\npause',
                encoding="utf-8",
            )
            subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", str(bat)],
                cwd=str(root),
            )
            return True, "Se abrió una terminal. JupyterLab se abrirá en el navegador automáticamente."
        else:
            subprocess.Popen(
                ["xterm", "-e", f"cd {root} && python -m jupyterlab --config={config_path}"],
                cwd=str(root),
                start_new_session=True,
            )
            return True, "Se abrió una terminal. JupyterLab se abrirá automáticamente."
    except Exception as e:
        return False, str(e)


st.markdown("""
<style>[data-testid="stSidebar"] { min-width: 12rem !important; max-width: 12rem !important; }</style>
""", unsafe_allow_html=True)

st.title("Notebooks del curso")

with st.expander("📖 Cómo usar", expanded=True):
    st.markdown("""
    1. Hacé clic en **Abrir terminal con JupyterLab** (o ejecutá el comando manualmente).
    2. Se abrirá una ventana de terminal y JupyterLab se abrirá **automáticamente en una nueva pestaña del navegador**.
    3. Navegá a la carpeta del eje (tabla de abajo) y abrí el `.ipynb`.
    4. Ejecutá Jupyter **desde la raíz del repo** para que `from Codigo.…` funcione.
    """)

st.subheader("Índice de ejes")
for titulo, ruta, detalle in _EJES:
    st.markdown(f"- **{titulo}** — `{ruta}`  \n  {detalle}")

st.caption("Las páginas de la app (Propiedades, Payoffs, Market Data, Modelos de Pricing, …) apuntan a estos notebooks.")

st.divider()

jupyter_port = _find_jupyter_port()
port = jupyter_port if jupyter_port is not None else 8888
jupyter_url = f"http://127.0.0.1:{port}"

if jupyter_port is not None:
    st.success(f"JupyterLab está corriendo en el puerto {port}.")
else:
    st.warning("JupyterLab no está corriendo. Inicialo con el botón de abajo.")

st.markdown(f"### [Abrir JupyterLab →]({jupyter_url})")
st.caption(f"URL: {jupyter_url} — Si JupyterLab usa otro puerto, copiá la URL que aparece en la terminal.")

st.divider()

if st.button("Abrir terminal con JupyterLab", type="primary"):
    ok, msg = _launch_jupyter_in_new_terminal()
    if ok:
        st.success(msg)
        st.info("Cuando JupyterLab abra, andá a `Notebooks/ejes/`.")
    else:
        st.error(f"No se pudo abrir la terminal: {msg}")
        st.code(
            "python -m jupyterlab --config=webapp/jupyter_server_config.py",
            language="bash",
        )
