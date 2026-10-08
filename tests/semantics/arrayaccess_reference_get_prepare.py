from pathlib import Path
import base64
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from error_handler_run import ENV, describe
from recorded_worker import Worker
from arrayaccess_reference_get_cases import CASES as AUTHOR
from arrayaccess_reference_get_review_cases import CASES as REVIEW


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
            for key, command in [('head', ['rev-parse', 'HEAD']),
                                 ('tree', ['rev-parse', 'HEAD^{tree}']),
                                 ('status', ['status', '--porcelain'])]}


before = revision()
assert not before['status']
cases = {case['id']: case for case in AUTHOR + REVIEW}
selected = sys.argv[1:] or list(cases)
assert len(selected) == len(set(selected)) and all(name in cases for name in selected)
store = ROOT / '.tools/arrayaccess-reference-get'
store.mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='prepared-', dir=store))
print(out, flush=True)
modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
paths = [ROOT / name for name in modules] + [Path(__file__),
    ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/profile.json',
    ROOT / 'tests/semantics/arrayaccess_reference_get_cases.py',
    ROOT / 'tests/semantics/arrayaccess_reference_get_review_cases.py',
    ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/static_types.py',
    ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'frontend/worker.php',
    ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe']
watched = {str(path): describe(path) for path in paths}
rows, failure = [], None
frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
    'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
try:
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        for name in selected:
            case = cases[name]
            source = out / (name + '.php')
            source.write_text(case['source'])
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            fixture = out / (name + '.program')
            fixture.write_text(checked['fixture'])
            for path in (source, fixture):
                watched[str(path)] = describe(path)
            rows.append({'id': name, 'source': str(source), 'fixture': str(fixture),
                         'expected_stdout': case['expected_stdout'], 'passed': True})
            print(name, 'checked', flush=True)
    finally:
        adapter.close()
except BaseException as error:
    failure = {'type': type(error).__name__, 'message': str(error)}
finally:
    frontend.close()
loader = out / 'initial.watsup'
if rows:
    first = rows[0]
    loader.write_text('dec $main() : bool\ndef $main() = true\n'
        + '  -- if S = $php_run(' + Path(first['fixture']).read_text() + ', 0, '
        + json.dumps(base64.b64encode(first['source'].encode()).decode()) + ')\n'
        + '  -- if S.COMPLETION = BUDGET\n'
        + '  -- if $call_current_valid(S)\n'
        + '  -- if $call_frames_valid(S, S.FRAMES)\n'
        + '  -- if $call_descriptors_valid(S)\n'
        + '  -- if $heap_valid($heap_graph(S))\n')
    watched[str(loader)] = describe(loader)
after = revision()
stable = before == after and watched == {name: describe(name) for name in watched}
passed = failure is None and len(rows) == len(selected) and stable
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before,
    'revision_after': after, 'modules': len(modules), 'inputs': watched, 'inputs_stable': stable,
    'selection': selected, 'records': rows, 'loader': str(loader), 'failure': failure,
    'scope': 'Original bytes to checked AST fixtures only; no compiler/source/state execution credit'}, indent=2) + '\n')
raise SystemExit(0 if passed else 1)
