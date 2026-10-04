#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Running zcabs check..."
python -m zcabs check

echo "==> Running zcabs unit tests..."
python -m unittest discover -s tests -v

echo "==> All zcabs checks passed!"
