Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   🛡️ AEGIS-AI | SAFETY EYE COMMAND CENTER" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Launching... (Please wait a few seconds)"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    & $venvPython -m streamlit run (Join-Path $scriptDir "app.py")
} else {
    python -m streamlit run (Join-Path $scriptDir "app.py")
}

Write-Host ""
Write-Host "Application session ended. Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
