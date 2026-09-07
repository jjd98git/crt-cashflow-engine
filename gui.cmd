@echo off
cd /d "%~dp0"
echo Starting the CRT Cashflow Engine GUI at http://localhost:8501 (close this window to stop it)
start "" cmd /c "timeout /t 4 /nobreak >nul & start "" http://localhost:8501"
.venv\Scripts\python -m streamlit run src\crt\gui\app.py
