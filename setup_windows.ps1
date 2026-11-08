param([switch]$Tutorials)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
function Check-Exit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE). Setup stopped." }
}
if (!(Test-Path '.venv\Scripts\python.exe')) {
    py -3.12 -m venv .venv
    Check-Exit 'Creating Python 3.12 environment'
}
$Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $Python -m pip install -e '.[dev]'
Check-Exit 'Installing national runner'
if ($Tutorials) {
    & $Python -m pip install -e '.[notebooks]'
    Check-Exit 'Installing common tutorial libraries'
    npm.cmd ci --ignore-scripts
    Check-Exit 'Installing the Earth Engine JavaScript SDK'
}
Write-Host 'Setup complete. Authenticate from the master notebook, then run the desired queue.'
Write-Host 'Do not run two notebooks/launchers concurrently.'
