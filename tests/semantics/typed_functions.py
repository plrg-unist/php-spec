"""Typed positional receives and value returns through checked source execution."""
from pathlib import Path
import json
import function_scope
ROOT = Path(__file__).resolve().parents[2]
CASES = {k: v.encode() for k, v in json.loads((ROOT / 'tests/semantics/typed_runtime_cases.json').read_text()).items()}
def main():
    before = set((ROOT / '.tools').glob('typed-functions-*'))
    if not function_scope.main(CASES, 'typed-functions', Path(__file__)):
        return False
    created = set((ROOT / '.tools').glob('typed-functions-*')) - before
    assert len(created) == 1
    raw = created.pop(); report = json.loads((raw / 'report.json').read_text())
    projections = []
    for row in report['records']:
        if row['id'] not in ('deferred-string-int-cache-weak', 'deferred-string-int-cache-strict', 'typed-default-ref-fresh-cache'):
            continue
        state = json.loads((raw / row['id'] / 'state.json').read_text())['state']
        assert len(state['DEFAULTCACHE']) == 1
        cache = state['DEFAULTCACHE'][0]
        assert cache['VALUE'] == {'tag': 'PSTRING', 'args': [['50']]}
        assert cache['CLASS'] == {'tag': 'PVSTRING', 'args': [True]}
        assert cache['ORIGIN'] == state['FUNCTIONS'][0]['DEFAULTS'][0]['ORIGIN']
        projections.append({'id': row['id'], 'uncoerced_cache': cache, 'assertions': 4, 'pass': True})
    report['cache_projections'] = projections
    report['projection_assertions'] = sum(row['assertions'] for row in projections)
    (raw / 'report.json').write_text(json.dumps(report, indent=2))
    if not report['selection']:
        (ROOT / 'coverage/semantics/typed-functions.json').write_text(json.dumps(report, indent=2))
    return True
if __name__ == '__main__': raise SystemExit(0 if main() else 1)
