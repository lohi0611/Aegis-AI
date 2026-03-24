@echo off
d:
cd \iomp\AI-Powered-Safety-At-Workplace-main
echo =======================================================
echo    🛡️ AEGIS-AI | SAFETY EYE COMMAND CENTER
echo =======================================================
echo.
echo Launching...

:: Use the exact command that we verified manually
".venv\Scripts\python.exe" -m streamlit run "dashboard\app.py"

:: Stay open if it finishes
pause
