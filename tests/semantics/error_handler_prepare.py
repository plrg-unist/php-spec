"""Check the fixed handler sources and AL fixtures without execution."""
from pathlib import Path
import base64
import json
import tempfile

from recorded_worker import Worker
from error_handler_cases import CASES as SOURCES
from error_handler_protocol import CASES, PREFIX

ROOT = Path(__file__).resolve().parents[2]


def main():
    from error_handler_run import describe, inputs, recorded
    before = inputs()
    store = ROOT / '.tools/error-handlers'
    store.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='prepared-', dir=store))
    print(out, flush=True)
    source_rows = []
    for name, source, expected, status in SOURCES:
        path = out / (name + '.php')
        path.write_bytes(source)
        source_rows.append({'id': name, 'path': str(path),
                            'expected_stdout_b64': base64.b64encode(expected).decode(),
                            'expected_status': status})
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    assert len(modules) == 187
    rows = []
    failure = None
    try:
        for name, source_id, stage, checks in CASES:
            directory = out / name
            directory.mkdir()
            source = next(Path(r['path']) for r in source_rows if r['id'] == source_id)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                                 directory / 'adapter')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                    assert parsed['accepted'], parsed
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok'], checked
                finally:
                    adapter.close()
            finally:
                frontend.close()
            path = json.dumps(base64.b64encode(str(source).encode()).decode())
            conditions = [
                'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + path + ')',
                'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
                r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
                'S = S_reached[.COMPLETION = NORMAL]',
                *checks,
                '$outputs(S_done.EVENTS) = [' + ','.join(map(str, next(s[2] for s in SOURCES if s[0] == source_id))) + ']',
            ]
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX.replace('STAGE', stage)
                               + '\ndec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in conditions))
            # Use the reviewed recorder to retain exits and kill owned groups.
            command = [str(ROOT / '.tools/p4spectec-algo-reused'), 'algo', *map(str, modules), str(fixture)]
            result = recorded(command, directory / 'compiler', 120)
            stdout = (directory / 'compiler.stdout').read_bytes()
            passed = result['exit'] == 0 and not result['timeout'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in stdout
            rows.append({'id': name, 'source_id': source_id, 'fixture': str(fixture),
                         'al': str(directory / 'compiler.stdout'), 'assertions': len(conditions),
                         'fixture_descriptor': describe(fixture),
                         'al_descriptor': describe(directory / 'compiler.stdout'),
                         'passed': passed})
            print(name, passed, len(conditions), flush=True)
            if not passed:
                break
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    after = inputs()
    passed = failure is None and before == after and len(rows) == len(CASES) and all(r['passed'] for r in rows)
    (out / 'report.json').write_text(json.dumps({'passed': passed, 'scope': 'parse/check/algo only',
        'zero_semantic_execution': True, 'sources': source_rows, 'records': rows, 'failure': failure,
        'inputs': before, 'inputs_after': after, 'inputs_stable': before == after}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
