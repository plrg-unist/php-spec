from pathlib import Path
import base64
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
assert len(sys.argv) == 2
prepared = json.loads(prepared_path.read_text())
assert prepared['passed']
before = revision()
assert before == prepared['revision'] and not before['status']
watched = dict(prepared['inputs'])
assert watched == {p: describe(p) for p in watched}
artifacts = ([prepared_path.parent / 'fixture.stdout', prepared_path.parent / 'fixture.stderr']
    if 'unchanged_semantic_compiler' in prepared
    else [prepared_path.parent / 'algo.stdout', prepared_path.parent / 'struct.stdout'])
for path in (prepared_path, Path(__file__), *artifacts):
    watched[str(path)] = describe(path)
out = Path(tempfile.mkdtemp(prefix='actual-run-', dir=ROOT / '.tools/arrayaccess-returned-append'))
print(out, flush=True)
profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
rows, failure = [], None
(out / 'TAKE.json').write_text(json.dumps({'revision': before, 'inputs': watched,
    'union': 'Current source plus returned-child append/eager/weak/provider interaction',
    'preparation': str(prepared_path), 'profile': profile, 'jobs': 1,
    'caps': {'strict_SL_initial': 120, 'native': 45, 'model_outer': 90, 'CLI': 60, 'steps': 100000},
    'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'], 'cwd': str(ROOT),
                    'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV}}, indent=2) + '\n')
try:
    loader = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, prepared['loader']], out / 'loader', 120)
    passed = (loader['exit'] == 0 and not loader['timeout'] and not loader['group_after']
        and (out / 'loader.stdout').read_bytes().strip() == b'true' and not (out / 'loader.stderr').read_bytes())
    rows.append({'id': 'strict_SL_initial', 'producer': loader, 'premises': 6, 'passed': passed})
    print('strict_SL_initial', passed, loader['elapsed'], flush=True)
    assert passed, 'strict SL initial'
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, prepared['source']], out / 'native', 45)
    stdout, stderr = (out / 'native.stdout').read_bytes(), (out / 'native.stderr').read_bytes()
    passed = native['exit'] == 0 and not native['timeout'] and not native['group_after'] and not stderr
    rows.append({'id': 'native', 'producer': native, 'passed': passed,
                 'stdout_b64': base64.b64encode(stdout).decode(), 'stderr_b64': base64.b64encode(stderr).decode()})
    print('native', passed, stdout.decode(errors='replace'), flush=True)
    assert passed, 'native'
    model_command = [str(ROOT / 'bin/php-semantics'), prepared['source']]
    model = recorded([*model_command, '--file-snapshot', prepared['provider'],
        '--steps', '100000', '--timeout', '60'], out / 'model', 90)
    raw = (out / 'model.stdout').read_bytes()
    observation = json.loads(raw) if raw else None
    passed = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
        and not (out / 'model.stderr').read_bytes() and observation
        and observation.get('status') == 'normal' and observation.get('frontend') == 'accepted'
        and observation.get('checked') == 'program' and observation.get('exit_status') == 0
        and observation.get('stdout') == base64.b64encode(stdout).decode()
        and observation.get('stderr') == base64.b64encode(stderr).decode())
    rows.append({'id': 'model', 'producer': model, 'passed': bool(passed), 'observation': observation})
    print('model', bool(passed), observation and observation.get('status'), model['elapsed'], flush=True)
    assert passed, 'model'
except BaseException as error:
    failure = {'type': type(error).__name__, 'message': str(error)}
after = revision()
stable = watched == {p: describe(p) for p in watched} and before == after
groups = {str(r['producer']['pgid']): group(r['producer']['pgid']) for r in rows}
passed = (failure is None and len(rows) == 3 and all(r['passed'] for r in rows)
    and stable and all(not members for members in groups.values()))
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before, 'revision_after': after,
    'preparation': str(prepared_path), 'source': prepared['source'], 'companion': prepared['companion'],
    'provider': prepared['provider'], 'records': rows, 'failure': failure,
    'inputs_stable': stable, 'groups_after': groups, 'jobs': 1,
    'scope': 'Current original-source interaction and strict SL initialization; no historical renewal'}, indent=2) + '\n')
raise SystemExit(0 if passed else 1)
