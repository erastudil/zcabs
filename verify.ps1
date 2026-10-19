$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    $env:PYTHONPATH = Join-Path $PSScriptRoot "src"

    Write-Host "==> [1/3] Running zcabs check..."
    python -m zcabs check
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "==> [2/3] Running zcabs Python unit tests..."
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "==> [3/3] Running zcabs JavaScript unit tests..."
    node --test js/zcabs.test.js
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Write-Host "==> All zcabs Python + JS checks passed (exit 0)!"
} finally {
    Pop-Location
}
