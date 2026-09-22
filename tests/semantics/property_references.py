#!/usr/bin/env python3
"""Replay retained property-reference originals and one derived source control."""
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
CASES = json.loads((ROOT / 'tests/semantics/property_references_cases.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(match):
    selected = [row for row in CASES if match in row['id'] and (row.get('admitted', True) or match)]
    assert selected, 'no source controls selected'
    before = types.syntax_validation.implementation_fingerprint()
    direct_paths = [Path(__file__), ROOT / 'tests/semantics/property_references_cases.json',
                    ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json']
    direct = {str(path.relative_to(ROOT)): sha(path) for path in direct_paths}
    out = Path(tempfile.mkdtemp(prefix='property-references-', dir=ROOT / '.tools'))
    records = []
    environment = os.environ.copy()
    environment.update(LC_ALL='C', TZ='UTC')
    for row in selected:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256'], row['id']
        command = [str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '30']
        result = subprocess.run(command, cwd=directory, env=environment,
                                capture_output=True, timeout=35)
        (directory / 'runner.stdout').write_bytes(result.stdout)
        (directory / 'runner.stderr').write_bytes(result.stderr)
        (directory / 'runner.status.json').write_text(json.dumps({'exit_status': result.returncode}))
        try:
            actual = json.loads(result.stdout)
        except json.JSONDecodeError:
            actual = {'status': 'runner_failure', 'stdout': '', 'stderr': '', 'exit_status': None}
        expected = {
            'stdout': row['stdout_base64'],
            'stderr': base64.b64encode(row['stderr'].replace('{FILE}', str(source)).encode()).decode(),
            'exit_status': row['exit_status'],
        }
        passed = result.returncode == 0 and actual.get('status') == row['status'] and all(
            actual.get(key) == value for key, value in expected.items())
        records.append({'id': row['id'], 'pass': passed, 'native_profile': row['native_profile'],
                        'oracle_exact': row.get('oracle_exact', True),
                        'source_sha256': row['source_sha256'], 'expected': expected, 'actual': actual,
                        'runner_exit_status': result.returncode})
        print(row['id'], passed, actual.get('status'), flush=True)
    assert before == types.syntax_validation.implementation_fingerprint(), 'implementation changed during run'
    assert all(sha(ROOT / path) == digest for path, digest in direct.items()), 'direct input changed during run'
    report = {'result': 'pass' if all(row['pass'] for row in records) else 'fail',
              'selection': match, 'selected_cases': len(selected), 'catalogue_cases': len(CASES),
              'fingerprint': before, 'direct_inputs': direct, 'raw': str(out), 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match) else 1)
