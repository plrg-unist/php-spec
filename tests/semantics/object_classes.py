#!/usr/bin/env python3
"""Named empty class activation, allocation, identity, and core object errors."""
from pathlib import Path
import json
import function_scope as scope

CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('object_classes_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'object-classes', Path(__file__)) else 1)
