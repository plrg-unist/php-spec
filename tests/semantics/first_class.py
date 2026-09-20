#!/usr/bin/env python3
"""First-class conversion of named user functions and existing callable values."""
from pathlib import Path
import json
import function_scope as scope

CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('first_class_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'first-class', Path(__file__)) else 1)
