# demo package

A tiny package with an entry point in `main.py` and a `compute` helper.

`compute` used to live in `utils.py`. It moved to `utils_v2.py`; `utils.py`
now raises on import so nothing keeps importing the old path by accident.
Callers should import `compute` from `utils_v2`.
