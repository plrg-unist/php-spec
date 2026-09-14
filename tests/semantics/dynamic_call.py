#!/usr/bin/env python3
"""String-named user calls, evaluation order, references and lookup errors."""
from pathlib import Path
import json
import function_scope as scope
CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('dynamic_call_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'dynamic-call', Path(__file__)) else 1)
