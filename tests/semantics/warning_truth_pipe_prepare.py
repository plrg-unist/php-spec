"""Parse/check and elaborate the held-PIPE truth fixture without execution."""
from pathlib import Path
import base64
import json
import tempfile

from recorded_worker import Worker
from warning_truth_pipe import SOURCES
from warning_truth_pipe import CASES, PREFIX
from warning_truth_pipe_run import ROOT, describe, inputs, recorded, revision


def main():
    assert Path.cwd() == ROOT
    before = inputs()
    store = ROOT / '.tools/warning-truth-pipe'
    store.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='prepared-', dir=store))
    print(out, flush=True)
    sources = []
    for name, source, expected, status in SOURCES:
        path = out / (name + '.php')
        path.write_bytes(source)
        sources.append({'id': name, 'path': str(path), 'expected_status': status,
                        'expected_stdout_b64': base64.b64encode(expected).decode()})
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    assert len(modules) == len(set(modules))
    assert ROOT / 'spec/semantics/209-warning-truth-continuations.watsup' in modules
    rows, failure = [], None
    try:
        for name, source_id, stage, checks in CASES:
            directory = out / name
            directory.mkdir()
            source = next(Path(r['path']) for r in sources if r['id'] == source_id)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')],
                              directory / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                    assert parsed['accepted'], parsed
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok'], checked
                finally:
                    adapter.close()
            finally:
                frontend.close()
            path = '[' + ','.join(map(str, bytes(source))) + ']'
            cwd = '[' + ','.join(map(str, bytes(ROOT))) + ']'
            expected = next(s[2] for s in SOURCES if s[0] == source_id)
            conditions = ['S_initial = $php_file_run(' + checked['fixture'] + ', 0, ' + path + ', ' + cwd + ')',
                          'S_initial.COMPLETION = BUDGET',
                          'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
                          r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
                          'S = S_reached[.COMPLETION = NORMAL]', *checks,
                          '$outputs(S_done.EVENTS) = [' + ','.join(map(str, expected)) + ']']
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX.replace('STAGE', stage)
                + '\ndec $main() : bool\ndef $main() = true\n'
                + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in conditions))
            producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *map(str, modules), str(fixture)],
                                directory / 'compiler', 120)
            al = directory / 'compiler.stdout'
            passed = (producer['exit'] == 0 and not producer['timeout']
                      and not (directory / 'compiler.stderr').read_bytes()
                      and b'\ndef $main : bool =\n' in al.read_bytes())
            rows.append({'id': name, 'source_id': source_id, 'fixture': str(fixture), 'al': str(al),
                         'fixture_descriptor': describe(fixture), 'al_descriptor': describe(al),
                         'assertions': len(conditions), 'passed': passed, 'producer': producer})
            print(name, passed, len(conditions), flush=True)
            assert passed, name
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    after = inputs()
    passed = failure is None and before == after and len(rows) == len(CASES) and all(r['passed'] for r in rows)
    (out / 'report.json').write_text(json.dumps({'passed': passed,
        'scope': 'parse/check/algo only; zero target/model/state', 'revision_context': revision(),
        'sources': sources, 'records': rows, 'failure': failure,
        'inputs': before, 'inputs_after': after, 'inputs_stable': before == after}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
