#!/usr/bin/env bash
set -uo pipefail

wd="${1:-.}"
cd "$wd" 2>/dev/null || { echo "SCORE=0/3 FAIL"; exit 0; }

out="$(python3 -m unittest -v test_clamp 2>&1)"
passed="$(printf '%s\n' "$out" | grep -cE '\.\.\. ok')"
[ -z "$passed" ] && passed=0

if [ "$passed" -eq 3 ]; then
  echo "SCORE=3/3 PASS"
else
  echo "SCORE=${passed}/3 FAIL"
fi
exit 0
