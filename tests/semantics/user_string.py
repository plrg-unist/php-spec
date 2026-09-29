#!/usr/bin/env python3
"""Original-source differential controls for user object string conversion."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / 'tests/semantics/user_string_cases.json'
PHP = ROOT / '.tools/php/bin/php'
MODEL = ROOT / 'bin/php-semantics'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(match):
    rows = [row for row in json.loads(CASES.read_text()) if match in row['id']]
    assert rows, 'no user-string source selected'
    fingerprint = types.syntax_validation.implementation_fingerprint()
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CASES,
               Path(__file__), MODEL, ROOT / 'tests/semantics/profile.json']
    direct = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    out = Path(tempfile.mkdtemp(prefix='user-string-', dir=ROOT / '.tools'))
    results = []
    for row in rows:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256'], row['id']
        native = subprocess.run([PHP, '-n', *flags, source], cwd=directory,
                                env=env, capture_output=True, timeout=45)
        model = subprocess.run([MODEL, source, '--steps', '100000', '--timeout', '45'],
                               cwd=directory, env=env, capture_output=True, timeout=55)
        (directory / 'native.stdout').write_bytes(native.stdout)
        (directory / 'native.stderr').write_bytes(native.stderr)
        (directory / 'model.stdout').write_bytes(model.stdout)
        (directory / 'model.stderr').write_bytes(model.stderr)
        actual = json.loads(model.stdout)
        if row['expected_model'] == 'unsupported':
            passed = actual.get('status') == 'unsupported' and model.returncode == 1
        else:
            passed = (model.returncode == 0 and not model.stderr and
                      actual.get('status') == row['expected_model'] and
                      base64.b64decode(actual['stdout']) == native.stdout and
                      base64.b64decode(actual['stderr']) == native.stderr and
                      actual['exit_status'] == native.returncode)
        results.append({'id': row['id'], 'pass': passed, 'source_sha256': row['source_sha256'],
                        'native_exit': native.returncode, 'model_status': actual.get('status'),
                        'model_reason': actual.get('reason')})
        print(row['id'], passed, actual.get('status'), flush=True)
    assert fingerprint == types.syntax_validation.implementation_fingerprint()
    assert all(sha(ROOT / name) == digest for name, digest in direct.items())
    report = {'result': 'pass' if all(row['pass'] for row in results) else 'fail',
              'selection': match, 'fingerprint': fingerprint, 'direct_inputs': direct,
              'raw': str(out), 'records': results}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match) else 1)
