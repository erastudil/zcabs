$ErrorActionPreference = "Stop"

Write-Host "==> Running zcabs check..."
python -m zcabs check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Running zcabs unit tests..."
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> All zcabs checks passed!"
