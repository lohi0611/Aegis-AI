cd /d "%~dp0"
echo =======================================================
echo    🛡️ AEGIS-AI | SAFETY EYE COMMAND CENTER
echo =======================================================
echo.
echo Launching AEGIS Safety Platform...
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run "app.py"
) else (
    python -m streamlit run "app.py"
)

pause
