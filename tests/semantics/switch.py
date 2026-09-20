#!/usr/bin/env python3
"""Switch selection, diagnostics, nesting, and saved-subject ownership."""
from pathlib import Path
import json
import function_scope as scope

CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('switch_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'switch', Path(__file__)) else 1)
