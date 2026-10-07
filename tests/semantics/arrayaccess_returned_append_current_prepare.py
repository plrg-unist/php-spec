from pathlib import Path
import base64
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from error_handler_run import ENV, describe, group, recorded
from recorded_worker import Worker


def b64(value):
    return base64.b64encode(value).decode()


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
        for key, command in [('head', ['rev-parse', 'HEAD']), ('tree', ['rev-parse', 'HEAD^{tree}']),
                             ('status', ['status', '--porcelain'])]}


before = revision()
assert not before['status']
store = ROOT / '.tools/arrayaccess-returned-append'
store.mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='actual-prepared-', dir=store))
print(out, flush=True)
source = ROOT / 'tests/semantics/arrayaccess-returned-append-current/current.php'
companion = source.parent / 'Array'
assert not (ROOT / 'Array').exists()
snapshot = out / 'snapshot.json'
snapshot.write_text(json.dumps({'version': 2, 'main': b64(bytes(source)),
    'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'entries': [{
        'caller': b64(bytes(source)), 'requested': b64(b'Array'), 'cwd': b64(bytes(ROOT)),
        'include_path': b64(b'.:'), 'status': 'opened', 'resolved': b64(bytes(companion)),
        'opened': b64(bytes(companion)), 'source': b64(companion.read_bytes())}],
    'chdir_entries': []}, indent=2) + '\n')
frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
    'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
try:
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        adapter.close()
finally:
    frontend.close()
loader = out / 'initial.watsup'
loader.write_text('dec $main() : bool\ndef $main() = true\n'
    + '  -- if S = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(b64(bytes(source))) + ')\n'
    + '  -- if S.COMPLETION = BUDGET\n'
    + '  -- if $call_current_valid(S)\n'
    + '  -- if $call_frames_valid(S, S.FRAMES)\n'
    + '  -- if $call_descriptors_valid(S)\n'
    + '  -- if $heap_valid($heap_graph(S))\n')
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
paths = [Path(p) for p in modules] + [ROOT / 'spec/semantics/modules.json', source, companion, snapshot,
    loader, Path(__file__), ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
    ROOT / '.tools/spectec/bin/p4spectec', ROOT / '_build/default/adapter/main.exe',
    ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'tests/semantics/numeric_runner.ml',
    ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'bin/php-semantics']
watched = {str(p): describe(p) for p in paths}
rows, failure = [], None
try:
    for stage in ('algo', 'struct'):
        producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), stage, *modules], out / stage, 120)
        emitted = (out / (stage + '.stdout')).read_bytes()
        markers = {name: ('def $' + name).encode() in emitted
            for name in ('php_run', 'access_finish_task', 'access_set_plan', 'eager_source_origin', 'weakref_at',
                         'scope_check_result', 'call_entry_scope_checked', 'call_entry_descriptors_checked',
                         'error_handler_invoke_known', 'compiled_argument_access', 'ppaccess_at')}
        passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
            and not (out / (stage + '.stderr')).read_bytes() and all(markers.values()))
        rows.append({'id': stage, 'producer': producer, 'markers': markers,
                     'emitted_bytes': len(emitted), 'passed': passed})
        print(stage, passed, len(emitted), flush=True)
        assert passed, stage
except BaseException as error:
    failure = {'type': type(error).__name__, 'message': str(error)}
after = revision()
stable = watched == {path: describe(path) for path in watched} and before == after
groups = {str(r['producer']['pgid']): group(r['producer']['pgid']) for r in rows}
passed = failure is None and len(rows) == 2 and all(r['passed'] for r in rows) and stable and all(not x for x in groups.values())
(out / 'report.json').write_text(json.dumps({'passed': passed,
    'scope': 'Current returned-child append compiler/frontend/provider preparation only; no source/state execution credit',
    'revision': before, 'revision_after': after, 'modules': len(modules), 'inputs': watched,
    'inputs_stable': stable, 'source': str(source), 'companion': str(companion),
    'provider': str(snapshot), 'loader': str(loader), 'records': rows,
    'groups_after': groups, 'failure': failure, 'jobs': 1, 'compiler_cap_seconds': 120}, indent=2) + '\n')
raise SystemExit(0 if passed else 1)
