#!/usr/bin/env python3
"""Original-source differential controls for ordinary-frame argument introspection."""
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
CASES = ROOT / 'tests/semantics/argument_introspection_cases.json'
PHP = ROOT / '.tools/php/bin/php'
MODEL = ROOT / 'bin/php-semantics'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(match):
    rows = [row for row in json.loads(CASES.read_text()) if match in row['id']]
    assert rows, 'no argument-introspection source selected'
    fingerprint = types.syntax_validation.implementation_fingerprint()
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CASES,
               Path(__file__), MODEL, ROOT / 'tests/semantics/profile.json']
    direct = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    out = Path(tempfile.mkdtemp(prefix='argument-introspection-', dir=ROOT / '.tools'))
    results = []
    for row in rows:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        assert sha(source) == row['source_sha256'], row['id']
        native_command = [str(PHP), '-n', *flags, str(source)]
        model_command = [str(MODEL), str(source), '--steps', '100000', '--timeout', '45']
        files = row.get('files', {})
        for name, content in files.items():
            (directory / name).write_bytes(content.encode())
        if files:
            b64 = lambda value: base64.b64encode(value).decode()
            entries = [{'caller': b64(os.fsencode(source)), 'requested': b64(name.encode()),
                        'status': 'opened', 'resolved': b64(os.fsencode(directory / name)),
                        'opened': b64(os.fsencode(directory / name)), 'source': b64(content.encode())}
                       for name, content in files.items()]
            snapshot = {'version': 1, 'main': b64(os.fsencode(source)),
                        'cwd': b64(os.fsencode(directory)), 'include_path': b64(b'.:'),
                        'entries': entries}
            snapshot_path = directory / 'snapshot.json'
            snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
            model_command += ['--file-snapshot', str(snapshot_path)]
        (directory / 'commands.json').write_text(json.dumps(
            {'native': native_command, 'model': model_command, 'cwd': str(directory),
             'profile': profile, 'LC_ALL': 'C', 'TZ': 'UTC',
             'files': {name: hashlib.sha256(content.encode()).hexdigest()
                       for name, content in files.items()}}, indent=2) + '\n')
        native = subprocess.run(native_command, cwd=directory, env=env,
                                capture_output=True, timeout=45)
        model = subprocess.run(model_command, cwd=directory, env=env,
                               capture_output=True, timeout=55)
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
                      actual.get('frontend') == 'accepted' and actual.get('checked') == 'program' and
                      base64.b64decode(actual['stdout']) == native.stdout and
                      base64.b64decode(actual['stderr']) == native.stderr and
                      actual['exit_status'] == native.returncode)
        results.append({'id': row['id'], 'pass': passed, 'source_sha256': row['source_sha256'],
                        'native_exit': native.returncode, 'model_exit': model.returncode,
                        'control': row['expected_model'] == 'unsupported',
                        'frontend': actual.get('frontend'), 'checked': actual.get('checked'),
                        'raw_hashes': {name: sha(directory / name) for name in
                                       ('native.stdout', 'native.stderr', 'model.stdout', 'model.stderr', 'commands.json')},
                        'model_status': actual.get('status'),
                        'model_reason': actual.get('reason')})
        print(row['id'], passed, actual.get('status'), flush=True)
    assert fingerprint == types.syntax_validation.implementation_fingerprint()
    assert all(sha(ROOT / name) == digest for name, digest in direct.items())
    report = {'result': 'pass' if all(row['pass'] for row in results) else 'fail',
              'selection': match, 'fingerprint': fingerprint, 'direct_inputs': direct,
              'profile': profile, 'native_sha256': sha(PHP),
              'agreements': sum(row['pass'] and not row['control'] for row in results),
              'controls': sum(row['pass'] and row['control'] for row in results),
              'raw': str(out), 'records': results}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match) else 1)
