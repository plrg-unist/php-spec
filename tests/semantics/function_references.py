from pathlib import Path
import json
import function_scope
ROOT = Path(__file__).resolve().parents[2]
CASES = {k:v.encode() for k,v in json.loads((ROOT/'tests/semantics/function_reference_cases.json').read_text()).items()}
CASES.update({k:v.encode() for k,v in json.loads((ROOT/'tests/semantics/function_reference_runtime_cases.json').read_text()).items()})
if __name__ == '__main__':
    raise SystemExit(0 if function_scope.main(CASES, 'function-references', Path(__file__)) else 1)
