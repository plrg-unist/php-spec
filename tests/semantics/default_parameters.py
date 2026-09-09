"""Positional default receive, cache, ownership and error source profiles."""
from pathlib import Path
import json
import function_scope
ROOT = Path(__file__).resolve().parents[2]
CASES = {k: v.encode() for k, v in json.loads((ROOT / 'tests/semantics/default_runtime_cases.json').read_text()).items()}
def main():
    return function_scope.main(CASES, 'default-parameters', Path(__file__))
if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
