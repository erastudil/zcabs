#!/usr/bin/env bash
set -euo pipefail

echo "==> Running zcabs check..."
python -m zcabs check

echo "==> Running zcabs unit tests..."
python -m unittest discover -s tests -v

echo "==> All zcabs checks passed!"
