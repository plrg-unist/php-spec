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
from arrayaccess_returned_append_fiber_protocol import render, conditions


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
            for key, command in [('head', ['rev-parse', 'HEAD']),
                                 ('tree', ['rev-parse', 'HEAD^{tree}']),
                                 ('status', ['status', '--porcelain'])]}


before = revision()
assert not before['status']
source = ROOT / 'tests/semantics/arrayaccess-returned-append-current/paused-generator-fiber.php'
out = Path(tempfile.mkdtemp(prefix='fiber-prepared-', dir=ROOT / '.tools/arrayaccess-returned-append'))
print(out, flush=True)
modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
paths = [Path(path) for path in modules] + [source, Path(__file__), ROOT / 'tests/semantics/arrayaccess_returned_append_fiber_protocol.py',
    ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/error_handler_protocol.py',
    ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py',
    ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
    ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/spectec/bin/p4spectec']
watched = {str(path): describe(path) for path in paths}
frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
    'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
try:
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        adapter.close()
finally:
    frontend.close()
filename = json.dumps(base64.b64encode(bytes(source)).decode())
fixture = out / 'protocol.watsup'
fixture.write_text(render(checked['fixture'], filename))
watched[str(fixture)] = describe(fixture)
checks = conditions(checked['fixture'], filename)
producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)], out / 'compiler', 120)
emitted = (out / 'compiler.stdout').read_bytes()
passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
          and not (out / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in emitted)
after = revision()
stable = watched == {path: describe(path) for path in watched} and before == after
groups = {str(producer['pgid']): group(producer['pgid'])}
passed = passed and stable and all(not x for x in groups.values())
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before, 'revision_after': after,
    'inputs': watched, 'inputs_stable': stable, 'groups_after': groups, 'jobs': 1,
    'scope': 'Compiler-only same-source reached preparation; no renewed source/state credit',
    'execution_scope': 'New Fiber Set and paused Generator finalizer: authentic returned TEMP/old CELL, final target rejection, ownership and resumption',
    'records': [{'id': 'paused-generator-finalizer-keeps-returned-child-and-old-cell',
        'source_id': 'paused-generator-fiber', 'source': str(source), 'source_descriptor': describe(source),
        'fixture': str(fixture), 'fixture_descriptor': describe(fixture),
        'assertions': len(checks), 'passed': passed, 'producer': producer}]}, indent=2) + '\n')
print('compiler', passed, len(checks), flush=True)
raise SystemExit(0 if passed else 1)
