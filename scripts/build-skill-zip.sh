#!/usr/bin/env bash
# Packages the skill as dist/recipe-to-table.zip, the format Claude.ai accepts
# for uploaded skills (a folder with SKILL.md at its root).
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p dist
rm -f dist/recipe-to-table.zip
(cd skills && zip -qr ../dist/recipe-to-table.zip recipe-to-table -x '*/__pycache__/*' '*.pyc')
echo "Wrote dist/recipe-to-table.zip"
