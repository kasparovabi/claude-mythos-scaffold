#!/usr/bin/env bash
set -uo pipefail

wd="${1:-.}"
cd "$wd" 2>/dev/null || { echo "SCORE=0/1 FAIL"; exit 0; }

out="$(python3 main.py 2>/dev/null)"
if printf '%s\n' "$out" | grep -q '^RESULT=42$'; then
  echo "SCORE=1/1 PASS"
else
  echo "SCORE=0/1 FAIL"
fi
exit 0
