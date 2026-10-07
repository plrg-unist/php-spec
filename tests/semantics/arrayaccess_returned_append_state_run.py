from pathlib import Path
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from error_handler_run import ENV, describe, group, recorded


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
        for key, command in [('head', ['rev-parse', 'HEAD']), ('tree', ['rev-parse', 'HEAD^{tree}']),
                             ('status', ['status', '--porcelain'])]}


prepared_path = Path(sys.argv[1]).resolve()
prepared = json.loads(prepared_path.read_text())
assert prepared['passed'] and prepared['records']
assert all(describe(p) == d for p, d in prepared.get('inputs', {}).items())
before = revision()
assert before == prepared['revision'] and not before['status']
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
paths = [Path(p) for p in modules] + [ROOT / 'spec/semantics/modules.json', runner, prepared_path,
    Path(__file__), ROOT / 'tests/semantics/numeric_runner.ml', ROOT / 'tests/semantics/error_handler_run.py']
paths.extend(Path(p) for p in prepared.get('inputs', {}))
for row in prepared['records']:
    for key in ('source', 'fixture', 'companion'):
        if key not in row:
            continue
        assert describe(row[key]) == row[key + '_descriptor']
        paths.append(Path(row[key]))
    paths.extend([Path(row['fixture']).parent / 'compiler.stdout', Path(row['fixture']).parent / 'compiler.stderr'])
watched = {str(p): describe(p) for p in paths}
out = Path(tempfile.mkdtemp(prefix='owners-states-', dir=ROOT / '.tools/arrayaccess-returned-append'))
print(out, flush=True)
(out / 'TAKE.json').write_text(json.dumps({'revision': before, 'inputs': watched,
    'selection': [r['id'] for r in prepared['records']], 'jobs': 1, 'mode': 'strict SL',
    'cache': False, 'deterministic': True, 'cap_seconds_per_recipe': 300,
    'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'], 'cwd': str(ROOT),
                    'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV}}, indent=2) + '\n')
rows, failure = [], None
try:
    for row in prepared['records']:
        stem = out / row['id']
        producer = recorded([str(runner), '--sl', *modules, row['fixture']], stem, 300)
        passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
            and stem.with_suffix('.stdout').read_bytes().strip() == b'true'
            and not stem.with_suffix('.stderr').read_bytes())
        rows.append({'id': row['id'], 'source_id': row['source_id'], 'assertions': row['assertions'],
            'fixture': row['fixture'], 'producer': producer, 'passed': passed})
        print(row['id'], passed, producer['elapsed'], flush=True)
        assert passed, row['id']
except BaseException as error:
    failure = {'type': type(error).__name__, 'message': str(error)}
after = revision()
stable = watched == {p: describe(p) for p in watched} and before == after
groups = {str(r['producer']['pgid']): group(r['producer']['pgid']) for r in rows}
passed = failure is None and len(rows) == len(prepared['records']) and all(r['passed'] for r in rows) and stable and all(not x for x in groups.values())
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before, 'revision_after': after,
    'preparation': str(prepared_path), 'records': rows, 'failure': failure,
    'inputs_stable': stable, 'groups_after': groups, 'jobs': 1, 'mode': 'strict SL',
    'cache': False, 'deterministic': True, 'cap_seconds_per_recipe': 300,
    'scope': prepared.get('execution_scope', 'Selected source-reached returned-child append checks; no unrelated renewal')}, indent=2) + '\n')
raise SystemExit(0 if passed else 1)
