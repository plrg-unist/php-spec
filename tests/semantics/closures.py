#!/usr/bin/env python3
"""Real closure instances, explicit lexical captures, calls and PHP value behavior."""
from pathlib import Path
import json
import function_scope as scope
CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('closures_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'closures', Path(__file__)) else 1)
