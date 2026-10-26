#!/usr/bin/env python3
"""Public static method-name strings as pipe callables."""
from pathlib import Path
import json
import function_scope as scope

CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('pipe_static_string_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'pipe-static-string', Path(__file__), publish=False) else 1)
