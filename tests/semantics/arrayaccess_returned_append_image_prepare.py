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
from arrayaccess_returned_append_image_protocol import render


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
        for key, command in [('head', ['rev-parse', 'HEAD']), ('tree', ['rev-parse', 'HEAD^{tree}']),
                             ('status', ['status', '--porcelain'])]}


before = revision()
assert not before['status']
source = ROOT / 'tests/semantics/arrayaccess-returned-append-current/current.php'
out = Path(tempfile.mkdtemp(prefix='image-prepared-', dir=ROOT / '.tools/arrayaccess-returned-append'))
print(out, flush=True)
modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
paths = [Path(p) for p in modules] + [source, Path(__file__),
    ROOT / 'tests/semantics/arrayaccess_returned_append_image_protocol.py',
    ROOT / 'spec/semantics/modules.json', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
    ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/spectec/bin/p4spectec',
    ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/error_handler_run.py']
watched = {str(p): describe(p) for p in paths}
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
text, checks = render(checked['fixture'], source)
fixture = out / 'protocol.watsup'
fixture.write_text(text)
watched[str(fixture)] = describe(fixture)
producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)], out / 'compiler', 120)
emitted = (out / 'compiler.stdout').read_bytes()
markers = {name: ('def $' + name).encode() in emitted
    for name in ('main', 'compiled_argument_access', 'ppaccess_at')}
passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
    and not (out / 'compiler.stderr').read_bytes() and all(markers.values()))
after = revision()
stable = watched == {p: describe(p) for p in watched} and before == after
groups = {str(producer['pgid']): group(producer['pgid'])}
passed = passed and stable and all(not x for x in groups.values())
(out / 'report.json').write_text(json.dumps({'passed': passed, 'revision': before, 'revision_after': after,
    'inputs': watched, 'inputs_stable': stable, 'groups_after': groups,
    'records': [{'id': 'image-source-reached-access-tail', 'source_id': 'actual309-broad-compiled-image',
        'source': str(source), 'source_descriptor': describe(source),
        'fixture': str(fixture), 'fixture_descriptor': describe(fixture),
        'assertions': len(checks), 'producer': producer, 'markers': markers, 'emitted_bytes': len(emitted), 'passed': passed}],
    'jobs': 1, 'scope': 'Affected source-reached image access and traversal fixture compilation only; no execution credit',
    'execution_scope': 'Genuine PPR argument, all access modes, recursive prefix/duplicate-priority/nonempty-miss access, incomplete completion and exact output order; no unrelated renewal'}, indent=2) + '\n')
print('image_fixture', passed, len(checks), len(emitted), flush=True)
raise SystemExit(0 if passed else 1)
