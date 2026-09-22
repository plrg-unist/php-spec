#!/usr/bin/env python3
"""Replay retained exit/die observable-tuple sources against the checked CLI."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import subprocess
import tempfile

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/exit_cases.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(match):
    selected = [row for row in CASES if match in row['id']]
    assert selected, 'no exit source controls selected'
    before = types.syntax_validation.implementation_fingerprint()
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
               ROOT / 'tests/semantics/exit_cases.json',
               ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json']
    direct = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='exit-expressions-', dir=ROOT / '.tools'))
    environment = os.environ.copy()
    environment.update(LC_ALL='C', TZ='UTC')
    records = []
    for row in selected:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256'], row['id']
        command = [str(ROOT / 'bin/php-semantics'), str(source),
                   '--steps', '100000', '--timeout', '45']
        result = subprocess.run(command, cwd=directory, env=environment,
                                capture_output=True, timeout=55)
        (directory / 'runner.stdout').write_bytes(result.stdout)
        (directory / 'runner.stderr').write_bytes(result.stderr)
        (directory / 'runner.status.json').write_text(json.dumps({'exit_status': result.returncode}) + '\n')
        try:
            actual = json.loads(result.stdout)
        except json.JSONDecodeError:
            actual = {'status': 'runner_failure'}
        assert row['native_claim'] == 'observable_tuple_only'
        passed = result.returncode == 0 and not result.stderr and actual.get('status') == row['model_status']
        passed = passed and actual.get('exit_status') == row['exit_status']
        stderr = base64.b64decode(row['stderr_template_base64']).replace(
            b'{FILE}', str(source).encode())
        passed = passed and actual.get('stdout') == row['stdout_base64']
        passed = passed and actual.get('stderr') == base64.b64encode(stderr).decode()
        records.append({'id': row['id'], 'pass': passed,
                        'native_claim': 'observable_tuple_only',
                        'model_status': row['model_status'],
                        'native_group': row['native_group'],
                        'native_raw_sha256': row['native_raw_sha256'],
                        'native_profile': row['native_profile'],
                        'source_sha256': row['source_sha256'],
                        'runner_exit_status': result.returncode,
                        'actual': actual})
        print(row['id'], passed, actual.get('status'), flush=True)
    assert before == types.syntax_validation.implementation_fingerprint(), 'implementation changed during run'
    assert all(sha(ROOT / name) == digest for name, digest in direct.items()), 'direct input changed during run'
    report = {'result': 'pass' if all(row['pass'] for row in records) else 'fail',
              'selection': match, 'selected_cases': len(selected),
              'catalogue_cases': len(CASES),
              'fingerprint': before, 'direct_inputs': direct, 'raw': str(out), 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match) else 1)
