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
            for key, command in [('head', ['rev-parse', 'HEAD']),
                                 ('tree', ['rev-parse', 'HEAD^{tree}']),
                                 ('status', ['status', '--porcelain'])]}


before = revision()
assert not before['status']
source = ROOT / 'tests/semantics/arrayaccess-returned-append-current/paused-generator-fiber.php'
out = Path(tempfile.mkdtemp(prefix='fiber-source-', dir=ROOT / '.tools/arrayaccess-returned-append'))
print(out, flush=True)
modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
paths = [ROOT / path for path in modules] + [source, Path(__file__),
    ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/profile.json',
    ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'bin/php-semantics',
    ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
    ROOT / '_build/default/adapter/main.exe']
watched = {str(path): describe(path) for path in paths}
profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
expected = b'G;S:1:11;A:parked;Q:resumed:11;F;C;R:25;E:25:31:1;'
rows, failure = [], None
try:
    native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], out / 'native', 45)
    stdout, stderr = (out / 'native.stdout').read_bytes(), (out / 'native.stderr').read_bytes()
    passed = (native['exit'] == 0 and not native['timeout'] and not native['group_after']
              and stdout == expected and not stderr)
    rows.append({'id': 'native', 'producer': native, 'passed': passed})
    print('native', passed, stdout.decode(errors='replace'), flush=True)
    assert passed, 'native expected tuple'
    model = recorded([str(ROOT / 'bin/php-semantics'), str(source),
                      '--steps', '100000', '--timeout', '60'], out / 'model', 90)
    raw = (out / 'model.stdout').read_bytes()
    observed = json.loads(raw) if raw else None
    passed = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
              and not (out / 'model.stderr').read_bytes() and observed
              and observed.get('frontend') == 'accepted' and observed.get('checked') == 'program'
              and observed.get('status') == 'normal' and observed.get('exit_status') == 0
              and observed.get('stdout') == base64.b64encode(stdout).decode()
              and observed.get('stderr') == base64.b64encode(stderr).decode())
    rows.append({'id': 'model', 'producer': model, 'passed': bool(passed), 'observation': observed})
    print('model', bool(passed), observed and observed.get('status'), model['elapsed'], flush=True)
    assert passed, 'model exact tuple'
except BaseException as error:
    failure = {'type': type(error).__name__, 'message': str(error)}
after = revision()
stable = watched == {path: describe(path) for path in watched} and before == after
groups = {str(row['producer']['pgid']): group(row['producer']['pgid']) for row in rows}
passed = failure is None and len(rows) == 2 and all(row['passed'] for row in rows) and stable and all(not x for x in groups.values())
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before, 'revision_after': after,
    'modules': len(modules), 'source': str(source), 'inputs': watched, 'inputs_stable': stable,
    'profile': profile, 'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'], 'cwd': str(ROOT),
        'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
    'records': rows, 'failure': failure, 'groups_after': groups, 'jobs': 1,
    'scope': 'One new original: final returned-child Set, Fiber suspension and paused Generator finalizer old-CELL readback'}, indent=2) + '\n')
raise SystemExit(0 if passed else 1)
