#!/usr/bin/env python3
"""Named PHP source calls, frame ownership and exact request-profile outcomes."""
from pathlib import Path
import json
import function_scope
ROOT = Path(__file__).resolve().parents[2]
CASES = {name: source.encode() for name, source in json.loads(
    (ROOT / 'tests/semantics/function_call_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if function_scope.main(CASES, 'function-calls', Path(__file__)) else 1)
