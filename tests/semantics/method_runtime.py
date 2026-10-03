#!/usr/bin/env python3
"""Replay retained instance method/constructor sources against the checked CLI."""
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
DEFAULT_CASES = ROOT / 'tests/semantics/method_runtime_cases.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(match, catalogue=DEFAULT_CASES):
    catalogue = Path(catalogue).resolve()
    data = json.loads(catalogue.read_text())
    cases = data['cases'] if isinstance(data, dict) else data
    shared_profile = data.get('native_profile') if isinstance(data, dict) else None
    selected = [row for row in cases if match in row['id']]
    assert selected, 'no method source controls selected'
    before = types.syntax_validation.implementation_fingerprint()
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
               catalogue,
               ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json']
    direct = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='method-runtime-', dir=ROOT / '.tools'))
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
        stdout_path, stderr_path = directory / 'runner.stdout', directory / 'runner.stderr'
        with stdout_path.open('wb') as stdout_stream, stderr_path.open('wb') as stderr_stream:
            try:
                result = subprocess.run(command, cwd=directory, env=environment,
                                        stdout=stdout_stream, stderr=stderr_stream, timeout=55)
                status = result.returncode
            except subprocess.TimeoutExpired:
                status = None
        stdout, stderr = stdout_path.read_bytes(), stderr_path.read_bytes()
        (directory / 'runner.status.json').write_text(json.dumps({'exit_status': status}) + '\n')
        try:
            actual = json.loads(stdout)
        except json.JSONDecodeError:
            actual = {'status': 'runner_failure'}
        passed = status == 0 and not stderr and actual.get('status') == row['status']
        passed = passed and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program' and actual.get('reason') is None
        passed = passed and actual.get('exit_status') == row['exit_status']
        stderr = base64.b64decode(row['stderr_template_base64']).replace(
            b'{FILE}', str(source).encode())
        passed = passed and actual.get('stdout') == row['stdout_base64']
        passed = passed and actual.get('stderr') == base64.b64encode(stderr).decode()
        records.append({'id': row['id'], 'pass': passed,
                        'native_group': row['native_group'],
                        'native_raw_sha256': row['native_raw_sha256'],
                        'native_profile': row.get('native_profile', shared_profile),
                        'source_sha256': row['source_sha256'],
                        'runner_exit_status': status,
                        'actual': actual})
        print(row['id'], passed, actual.get('status'), flush=True)
        if not passed:
            break
    assert before == types.syntax_validation.implementation_fingerprint(), 'implementation changed during run'
    assert all(sha(ROOT / name) == digest for name, digest in direct.items()), 'direct input changed during run'
    report = {'result': 'pass' if all(row['pass'] for row in records) else 'fail',
              'selection': match, 'selected_cases': len(selected),
              'catalogue_cases': len(cases),
              'completed_cases': len(records),
              'conditional_unrun': [row['id'] for row in selected[len(records):]],
              'fingerprint': before, 'direct_inputs': direct, 'raw': str(out), 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    parser.add_argument('--catalogue', type=Path, default=DEFAULT_CASES)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match, args.catalogue) else 1)
