# Config Jupyter para iframe en Streamlit (solo uso local)
c.ServerApp.tornado_settings = {
    "headers": {
        "Content-Security-Policy": "frame-ancestors 'self' http://localhost:8501 http://127.0.0.1:8501"
    }
}
c.ServerApp.allow_origin = "*"
# Sin token para acceso local (evita login al abrir en iframe)
c.ServerApp.token = ""
