# -*- coding: utf-8 -*-
"""Notebooks - JupyterLab en nueva pestaña."""
import socket
import subprocess
import sys
from pathlib import Path

_webapp = Path(__file__).resolve().parent.parent
if str(_webapp) not in sys.path:
    sys.path.insert(0, str(_webapp))

import streamlit as st

from i18n import render_language_selector

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

render_language_selector()

with st.expander("📖 Cómo usar", expanded=True):
    st.markdown("""
    1. Hacé clic en **Abrir terminal con JupyterLab** (o ejecutá el comando manualmente).
    2. Se abrirá una ventana de terminal y JupyterLab se abrirá **automáticamente en una nueva pestaña del navegador**.
    3. Usá esa pestaña para trabajar con los notebooks. Si la cerraste, usá el enlace de abajo.
    """)

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
    else:
        st.error(f"No se pudo abrir: {msg}")

st.markdown("""
**Comando manual** (desde la carpeta del proyecto):
```bash
python -m jupyterlab --config=webapp/jupyter_server_config.py
```
""")
