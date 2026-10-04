"""Compile the three fixed source-reached global-read/snapshot witnesses."""
from pathlib import Path
import base64
import json
import tempfile

from recorded_worker import Worker
from globals_warning_cases import CASES as SOURCES
from globals_warning_protocol import CASES, PREFIX
from globals_warning_run import ROOT, describe, facts, inputs, recorded, revision


def request_literal(q):
    def bs(value):
        return '([' + ','.join(map(str, base64.b64decode(value))) + '])'
    return ('{ ENV ([' + ','.join('(' + bs(k) + ',' + bs(v) + ')' for k, v in q['env'])
            + ']), ARGV ([' + ','.join(bs(x) for x in q['argv']) + ']), FILE ' + bs(q['file'])
            + ', SECONDS (' + q['seconds'] + '), MICROSECONDS ' + str(q['microseconds'])
            + ', VARIABLES ' + bs(q['variables']) + ', JIT true, CWD (' + bs(q['cwd']) + ') }')


def main():
    assert Path.cwd() == ROOT
    before = inputs()
    store = ROOT / '.tools/globals-warning'
    store.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='prepared-', dir=store))
    print(out, flush=True)
    sources, rows, failure = [], [], None
    for name, source, expected, status, request in SOURCES:
        path = out / (name + '.php')
        path.write_bytes(source)
        sources.append({'id': name, 'path': str(path), 'expected_status': status,
                        'expected_stdout_b64': base64.b64encode(expected).decode(),
                        'request': facts(path) if request else None})
    modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    try:
        for name, source_id, stage, checks in CASES:
            directory = out / name
            directory.mkdir()
            source = next(row for row in sources if row['id'] == source_id)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')],
                              directory / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(Path(source['path']).read_bytes()).decode()})
                    assert parsed['accepted'], parsed
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok'], checked
                finally:
                    adapter.close()
            finally:
                frontend.close()
            filename = json.dumps(base64.b64encode(source['path'].encode()).decode())
            call = ('$php_request_run(' + checked['fixture'] + ', 0, ' + filename + ', '
                    + request_literal(source['request']) + ')' if source['request'] else
                    '$php_run(' + checked['fixture'] + ', 0, ' + filename + ')')
            expected = next(s[2] for s in SOURCES if s[0] == source_id)
            conditions = ['S_initial = ' + call, 'S_initial.COMPLETION = BUDGET',
                          'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
                          r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
                          'S = S_reached[.COMPLETION = NORMAL]', *checks,
                          '$outputs(S_done.EVENTS) = [' + ','.join(map(str, expected)) + ']']
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in conditions))
            producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)], directory / 'compiler', 120)
            al = directory / 'compiler.stdout'
            passed = producer['exit'] == 0 and not producer['timeout'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in al.read_bytes()
            rows.append({'id': name, 'source_id': source_id, 'fixture': str(fixture), 'al': str(al),
                         'fixture_descriptor': describe(fixture), 'al_descriptor': describe(al),
                         'assertions': len(conditions), 'passed': passed, 'producer': producer})
            print(name, passed, len(conditions), flush=True)
            assert passed, name
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    after = inputs()
    passed = failure is None and before == after and len(rows) == len(CASES)
    (out / 'report.json').write_text(json.dumps({'passed': passed, 'scope': 'parse/check/algo only; no target/model/state',
        'revision': revision(), 'sources': sources, 'records': rows, 'failure': failure,
        'inputs': before, 'inputs_after': after, 'inputs_stable': before == after}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
