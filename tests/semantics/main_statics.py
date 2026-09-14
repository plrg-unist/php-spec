#!/usr/bin/env python3
"""Initial main-script static initialization, persistent references and global binding."""
from pathlib import Path
import json
import function_scope as scope
CASES = {name: source.encode() for name, source in json.loads(Path(__file__).with_name('main_statics_cases.json').read_text()).items()}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'main-statics', Path(__file__)) else 1)
