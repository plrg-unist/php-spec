#!/usr/bin/env python3
"""Public user __invoke objects as ordinary and optimized pipe callables."""
from pathlib import Path
import json
import function_scope as scope

CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('pipe_object_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'pipe-object', Path(__file__), publish=False) else 1)
