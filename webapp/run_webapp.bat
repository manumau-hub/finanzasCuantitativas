@echo off
echo Iniciando Streamlit (UCEMA QUANT) y JupyterLab...
cd /d %~dp0..
start cmd /k "cd /d %~dp0.. && python -m streamlit run webapp/UCEMA_QUANT.py"
