Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   🛡️ AEGIS-AI | SAFETY EYE COMMAND CENTER" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launching... (Please wait a few seconds)"

# Start the application using absolute paths
& "d:\iomp\AI-Powered-Safety-At-Workplace-main\.venv\Scripts\python.exe" -m streamlit run "d:\iomp\AI-Powered-Safety-At-Workplace-main\dashboard\app.py"

Write-Host ""
Write-Host "Application session ended. Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
