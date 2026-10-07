from pathlib import Path
import base64
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from recorded_worker import Worker
from error_handler_run import ENV, describe, group, recorded
from arrayaccess_returned_append_handler_protocol import render


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
        for key, command in [('head', ['rev-parse', 'HEAD']), ('tree', ['rev-parse', 'HEAD^{tree}']),
                             ('status', ['status', '--porcelain'])]}


source = ROOT / 'tests/semantics/arrayaccess-returned-append-current/current.php'
companion = source.parent / 'Array'
expected = b'W:O:C;I;G:1;OD;S:N:17:1;CD;R:25:17:31:29:0:0:0:0;'
before = revision()
assert not before['status']
out = Path(tempfile.mkdtemp(prefix='handler-prepared-', dir=ROOT / '.tools/arrayaccess-returned-append'))
print(out, flush=True)
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
paths = [Path(p) for p in modules] + [source, companion, Path(__file__),
    ROOT / 'tests/semantics/arrayaccess_returned_append_handler_protocol.py',
    ROOT / 'spec/semantics/171-include-runtime.watsup', ROOT / 'spec/semantics/207-error-handler-runtime.watsup', ROOT / 'spec/semantics/modules.json',
    ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe',
    ROOT / '.tools/spectec/bin/p4spectec', ROOT / 'tests/semantics/recorded_worker.py',
    ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/error_handler_protocol.py']
watched = {str(p): describe(p) for p in paths}
frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
    'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
try:
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        main = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert main['accepted'], main
        checked = adapter.request({'op': 'check', 'ast': main['ast'], 'fixture': True})
        assert checked['ok'], checked
        child = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file', 'profile': 'cli-raw-85',
            'requested': base64.b64encode(b'Array').decode(), 'resolved': base64.b64encode(bytes(companion)).decode(),
            'opened': base64.b64encode(bytes(companion)).decode(), 'source': base64.b64encode(companion.read_bytes()).decode()})
        assert child['accepted'], child
        checked_child = adapter.request({'op': 'check', 'ast': child['ast'], 'fixture': True})
        assert checked_child['ok'], checked_child
    finally:
        adapter.close()
finally:
    frontend.close()
text, checks = render(checked['fixture'], checked_child['fixture'], source, companion, ROOT, expected)
fixture = out / 'protocol.watsup'
fixture.write_text(text)
watched[str(fixture)] = describe(fixture)
producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)], out / 'compiler', 120)
emitted = (out / 'compiler.stdout').read_bytes()
markers = {name: ('def $' + name).encode() in emitted
    for name in ('main', 'seek', 'error_handler_invoke_known', 'file_open_resume_checked', 'file_parse_resume_checked')}
passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
    and not (out / 'compiler.stderr').read_bytes() and all(markers.values()))
after = revision()
stable = watched == {p: describe(p) for p in watched} and before == after
groups = {str(producer['pgid']): group(producer['pgid'])}
passed = passed and stable and all(not x for x in groups.values())
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before, 'revision_after': after,
    'inputs': watched, 'inputs_stable': stable, 'groups_after': groups,
    'records': [{'id': 'handler-source-reached-auth-and-budget', 'source_id': 'actual309-broad-warning-admission',
        'source': str(source), 'source_descriptor': describe(source), 'companion': str(companion),
        'companion_descriptor': describe(companion), 'fixture': str(fixture), 'fixture_descriptor': describe(fixture),
        'assertions': len(checks), 'producer': producer, 'markers': markers, 'emitted_bytes': len(emitted), 'passed': passed}],
    'jobs': 1, 'scope': 'New source-reached warning rejection/budget fixture compilation only; no execution credit',
    'execution_scope': 'Affected public warning admission and one-step callback/provider continuation on unchanged broad source; no unrelated renewal'}, indent=2) + '\n')
print('handler_fixture', passed, len(checks), len(emitted), flush=True)
raise SystemExit(0 if passed else 1)
