#!/usr/bin/env python3
"""Original call origins retain the result-use slots observed in pinned opcodes."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
import function_scope as scope
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/reference_return_demand.json'


def main():
    before = scope.q.t.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='reference-return-demand-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    files = [*modules, runner, Path(__file__), CATALOGUE,
             ROOT / 'tests/semantics/recorded_worker.py']
    inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (out / 'inputs.json').write_text(json.dumps({'fingerprint': before, 'files': inputs}, indent=2))
    for name in inputs:
        p = out / 'original-inputs' / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ROOT / name).read_bytes())
    frontend = Worker([str(scope.q.t.PHP), '-n', *scope.q.t.FLAGS, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend-wire')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter-wire')
    records, checks = [], []
    try:
        for i, row in enumerate(json.loads(CATALOGUE.read_text())['records']):
            source = base64.b64decode(row['source_base64'])
            assert hashlib.sha256(source).hexdigest() == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': row['source_base64']})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            (out / (row['id'] + '.checked.json')).write_text(json.dumps(checked))
            used = str(row['expected_result_used']).lower()
            checks += [f'S_{i} = $initial_state(NORMAL)[.SOURCES = [$pcsource(0, {checked["fixture"]})]]',
                       f'$reference_call_used(S_{i}, PORIGIN 0 ({row["pcpath"]})) = {used}']
            records.append(row)
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    fixture = out / 'demand.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
    command = [str(runner), *map(str, modules), str(fixture)]
    (out / 'runner.command.json').write_text(json.dumps(command))
    try:
        result = subprocess.run(command, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired as error:
        (out / 'runner.stdout').write_bytes(error.stdout or b'')
        (out / 'runner.stderr').write_bytes(error.stderr or b'')
        (out / 'runner.status.json').write_text(json.dumps({'status': 'timeout', 'seconds': 60}))
        raise
    (out / 'runner.stdout').write_bytes(result.stdout)
    (out / 'runner.stderr').write_bytes(result.stderr)
    (out / 'runner.status.json').write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, result
    assert before == scope.q.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'inputs': inputs, 'records': records,
              'assertions': len(checks), 'historical_runtime_boundaries': [r['id'] for r in records if r['runtime_boundary']],
              'scope': 'Source-demand projection only; two historical boundary labels describe original933 capture. Current runtime activation is tested separately.',
              'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    (ROOT / 'coverage/semantics/reference-return-demand.json').write_text(json.dumps(report, indent=2))
    print(len(records), 'opcode-derived source projections;', report['historical_runtime_boundaries'], flush=True)


if __name__ == '__main__':
    main()
