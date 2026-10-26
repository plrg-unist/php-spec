#!/usr/bin/env python3
"""Ordinary named function string carriers as pipe callables."""
from pathlib import Path
import json
import function_scope as scope

CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('pipe_named_carrier_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'pipe-named-carrier', Path(__file__), publish=False) else 1)
