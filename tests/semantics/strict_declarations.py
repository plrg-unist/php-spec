"""Strict directives preserve untyped execution and expose source code flags."""
from pathlib import Path
import json
import function_scope
ROOT = Path(__file__).resolve().parents[2]
CASES = {k: v.encode() for k, v in json.loads((ROOT / 'tests/semantics/strict_runtime_cases.json').read_text()).items()}
def main():
    before = set((ROOT / '.tools').glob('strict-declarations-*'))
    if not function_scope.main(CASES, 'strict-declarations', Path(__file__)):
        return False
    created = set((ROOT / '.tools').glob('strict-declarations-*')) - before
    assert len(created) == 1
    raw = created.pop(); report = json.loads((raw / 'report.json').read_text())
    records = []
    for row in report['records']:
        state = json.loads((raw / row['id'] / 'state.json').read_text())['state']
        expected = row['id'] != 'strict-zero-call'
        values = [code['STRICT'] for code in state['CODE']] + [function['CODE']['STRICT'] for function in state['FUNCTIONS']]
        assert values and all(value is expected for value in values), (row['id'], values)
        records.append({'id': row['id'], 'expected': expected, 'values': values, 'pass': True})
    report['strict_projections'] = records
    report['projection_assertions'] = sum(len(row['values']) for row in records)
    (raw / 'report.json').write_text(json.dumps(report, indent=2))
    if not report['selection']:
        (ROOT / 'coverage/semantics/strict-declarations.json').write_text(json.dumps(report, indent=2))
    print('Strict projections:', report['projection_assertions'])
    return True
if __name__ == '__main__': raise SystemExit(0 if main() else 1)
