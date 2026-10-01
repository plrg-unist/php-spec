#!/usr/bin/env python3
"""Check explicit Closure::call boundaries without claiming PHP agreement."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import tempfile

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / 'tests/semantics/closure_call_boundary_cases.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    rows = json.loads(CASES.read_text())
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CASES, Path(__file__),
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so']
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    fingerprint = types.syntax_validation.implementation_fingerprint()
    output = Path(tempfile.mkdtemp(prefix='closure-call-boundaries-', dir=ROOT / '.tools'))
    environment = os.environ.copy()
    environment.update(LC_ALL='C', TZ='UTC')
    results = []
    for row in rows:
        directory = output / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        assert digest(source) == row['source_sha256']
        process = subprocess.run([str(ROOT / 'bin/php-semantics'), str(source),
                                  '--steps', '100000', '--timeout', '45'],
                                 cwd=directory, env=environment, capture_output=True, timeout=55)
        (directory / 'runner.stdout').write_bytes(process.stdout)
        (directory / 'runner.stderr').write_bytes(process.stderr)
        actual = json.loads(process.stdout)
        passed = (process.returncode == 1 and not process.stderr and
                  actual.get('status') == 'unsupported' and
                  actual.get('reason') == row['reason'] and
                  actual.get('stdout') == row['stdout_base64'] and
                  actual.get('stderr') == row['stderr_template_base64'] and
                  actual.get('exit_status') is None and
                  actual.get('frontend') == 'accepted' and
                  actual.get('checked') == 'program')
        results.append({'id': row['id'], 'pass': passed, 'source_sha256': row['source_sha256'],
                        'native_raw_sha256': row['native_raw_sha256'],
                        'runner_exit_status': process.returncode, 'actual': actual})
        print(row['id'], passed, flush=True)
    stable = (before == {str(path.relative_to(ROOT)): digest(path) for path in watched} and
              fingerprint == types.syntax_validation.implementation_fingerprint())
    report = {'result': 'pass' if stable and all(x['pass'] for x in results) else 'fail',
              'stable': stable, 'fingerprint': fingerprint, 'inputs': before,
              'records': results, 'raw': str(output)}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(output, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
