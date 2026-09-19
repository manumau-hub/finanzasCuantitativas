@echo off
echo Iniciando Streamlit y JupyterLab...
echo.
echo Terminal 1: Streamlit en http://localhost:8501
echo Terminal 2: JupyterLab en http://localhost:8888
echo.
echo Abre http://localhost:8501 y ve a la pestana Notebooks
echo.
start cmd /k "cd /d %~dp0.. && python -m streamlit run webapp/app.py"
timeout /t 2 >nul
start cmd /k "cd /d %~dp0.. && python -m jupyterlab --config=webapp/jupyter_server_config.py"
