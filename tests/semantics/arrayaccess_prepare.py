"""Compile source-reached ArrayAccess results, notices and captured truth."""
from pathlib import Path
import base64
import json
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tests/semantics'))
from recorded_worker import Worker
from arrayaccess_cases import CASES as SOURCES, REACHED_SOURCES
SOURCES = SOURCES + REACHED_SOURCES
from arrayaccess_protocol import CASES, PREFIX
from error_handler_run import ROOT, ENV, describe, recorded
from warning_consumer_run import revision


def main():
    assert Path.cwd() == ROOT
    head = revision()
    assert not head['status'], head
    store = ROOT / '.tools/arrayaccess'
    store.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='prepared-', dir=store))
    print(out, flush=True)
    watched = {str(ROOT / p): describe(ROOT / p) for p in (
        'tests/semantics/arrayaccess_cases.py', 'tests/semantics/arrayaccess_protocol.py',
        'tests/semantics/arrayaccess_prepare.py', 'tests/semantics/profile.json',
        'spec/semantics/30-storage.watsup', 'spec/semantics/233-dimension-key-continuations.watsup',
        'spec/semantics/284-arrayaccess-dimensions.watsup', 'spec/semantics/178-interface-runtime.watsup',
        'spec/semantics/179-interface-methods.watsup', 'spec/semantics/180-interface-obligations.watsup',
        'spec/semantics/230-iterator-declaration-notices.watsup', 'spec/semantics/207-error-handler-runtime.watsup',
        'spec/semantics/39-ownership.watsup', 'spec/semantics/40-control.watsup',
        'spec/semantics/modules.json', '.tools/spectec/bin/p4spectec', '_build/default/adapter/main.exe',
        '.tools/php/bin/php', '.tools/php-file.so')}
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    rows, failure = [], None
    selected = set(sys.argv[1:]) or {c[0] for c in CASES}
    try:
        for name, source_id, stage, checks in CASES:
            if name not in selected:
                continue
            directory = out / name
            directory.mkdir()
            _, source, expected = next(c for c in SOURCES if c[0] == source_id)
            path = directory / 'source.php'
            path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
                    assert parsed['accepted'], parsed
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok'], checked
                finally:
                    adapter.close()
            finally:
                frontend.close()
            filename = json.dumps(base64.b64encode(str(path).encode()).decode())
            conditions = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + filename + ')',
                          'S_initial.COMPLETION = BUDGET', 'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
                          r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
                          'S = S_reached[.COMPLETION = NORMAL]', *checks,
                          '$outputs(S_done.EVENTS) = [' + ','.join(map(str, expected)) + ']']
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in conditions))
            producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)], directory / 'compiler', 120)
            al = directory / 'compiler.stdout'
            passed = producer['exit'] == 0 and not producer['timeout'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in al.read_bytes()
            rows.append({'id': name, 'source_id': source_id, 'fixture': str(fixture), 'al': str(al), 'source': str(path),
                         'fixture_descriptor': describe(fixture), 'al_descriptor': describe(al),
                         'assertions': len(conditions), 'passed': passed, 'producer': producer})
            print(name, passed, len(conditions), flush=True)
            assert passed, name
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    stable = watched == {p: describe(p) for p in watched}
    current = revision()
    passed = failure is None and len(rows) == len(selected) and all(r['passed'] for r in rows) and stable and head == current
    (out / 'report.json').write_text(json.dumps({'passed': passed, 'scope': 'compiler only; no target/model/state',
        'revision': head, 'inputs': watched, 'records': rows, 'failure': failure,
        'revision_after': current, 'inputs_stable': stable}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
