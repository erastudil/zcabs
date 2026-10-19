#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

echo "==> [1/3] Running zcabs check..."
python3 -m zcabs check

echo "==> [2/3] Running zcabs Python unit tests..."
python3 -m unittest discover -s tests -v

echo "==> [3/3] Running zcabs JavaScript unit tests..."
node --test js/zcabs.test.js

echo "==> All zcabs Python + JS checks passed (exit 0)!"
