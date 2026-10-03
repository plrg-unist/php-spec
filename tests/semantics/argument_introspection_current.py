#!/usr/bin/env python3
"""Original-source comparisons for the installed capture and SET union."""
import base64
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from argument_introspection_current_protocol import CASES
import static_types as types

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recorded(command, directory, label, cwd, environment, timeout):
    try:
        process = subprocess.run(command, cwd=cwd, env=environment,
                                 capture_output=True, timeout=timeout)
        stdout, stderr, status = process.stdout, process.stderr, process.returncode
        exit_record = {'exit_status': status}
    except subprocess.TimeoutExpired as error:
        stdout, stderr, status = error.stdout or b'', error.stderr or b'', None
        exit_record = {'exit_status': None, 'exception': 'TimeoutExpired', 'timeout_seconds': timeout}
    (directory / (label + '.stdout')).write_bytes(stdout)
    (directory / (label + '.stderr')).write_bytes(stderr)
    (directory / (label + '.exit.json')).write_text(json.dumps(exit_record) + '\n')
    return stdout, stderr, status


def main(catalogue=False, case=None):
    fingerprint = types.syntax_validation.implementation_fingerprint()
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    inputs = [ROOT / name for name in modules] + [
        ROOT / 'spec/semantics/modules.json', Path(__file__),
        ROOT / 'tests/semantics/argument_introspection_current_protocol.py',
        ROOT / 'tests/semantics/argument_introspection_cases.json',
        ROOT / 'tests/semantics/profile.json', ROOT / 'bin/php-semantics',
    ]
    hashes = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    if not catalogue:
        profile['include_path'] = '.:'
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    out = Path(tempfile.mkdtemp(prefix='argument-introspection-current-', dir=ROOT / '.tools'))
    b64 = lambda data: base64.b64encode(data).decode()
    rows = (json.loads((ROOT / 'tests/semantics/argument_introspection_cases.json').read_text()) if catalogue else
            [{'id': name, 'source': source.decode(), 'source_sha256': hashlib.sha256(source).hexdigest(),
              'expected_model': 'normal'} for name, source, _, _ in CASES])
    if case:
        rows = [row for row in rows if row['id'] == case]
    assert all(row['source_sha256'] != '667ec148271193333f7d82e78f3c74c8ffadba2ad28cf3a9e2e1611a2458017f'
               for row in rows)
    assert all(row['expected_model'] in {'normal', 'php_error', 'static_rejection', 'explicit_exit', 'unsupported'}
               for row in rows)
    print(out, flush=True)
    records = []
    for row in rows:
        name, source_bytes = row['id'], row['source'].encode()
        directory = out / name
        directory.mkdir()
        source = directory / ('source.php' if catalogue else 'main.php')
        source.write_bytes(source_bytes)
        assert sha(source) == row['source_sha256']
        cwd = directory if catalogue else ROOT
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
        model_command = [str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000',
                         '--timeout', '45' if catalogue else '60']
        files = row.get('files', {})
        for file_name, content in files.items():
            (directory / file_name).write_bytes(content.encode())
        snapshot = None
        if files or not catalogue:
            entries = [{'caller': b64(os.fsencode(source)), 'requested': b64(file_name.encode()),
                        'status': 'opened', 'resolved': b64(os.fsencode(directory / file_name)),
                        'opened': b64(os.fsencode(directory / file_name)), 'source': b64(content.encode())}
                       for file_name, content in files.items()]
            facts = {'version': 1 if catalogue else 2, 'main': b64(os.fsencode(source)),
                     'cwd': b64(os.fsencode(cwd)), 'include_path': b64(b'.:'), 'entries': entries}
            if not catalogue:
                facts['chdir_entries'] = []
            snapshot = directory / 'snapshot.json'
            snapshot.write_text(json.dumps(facts, sort_keys=True) + '\n')
            model_command += ['--file-snapshot', str(snapshot)]
        (directory / 'commands.json').write_text(json.dumps(
            {'native': native_command, 'model': model_command, 'cwd': str(cwd),
             'profile': profile, 'LC_ALL': 'C', 'TZ': 'UTC',
             'files': {name: hashlib.sha256(content.encode()).hexdigest() for name, content in files.items()}}, indent=2) + '\n')
        native = recorded(native_command, directory, 'native', cwd, environment, 45 if catalogue else 30)
        model = recorded(model_command, directory, 'model', cwd, environment, 55 if catalogue else 90)
        try:
            actual = json.loads(model[0])
        except ValueError:
            actual = {}
        control = row['expected_model'] == 'unsupported'
        if control:
            passed = model[2] == 1 and actual.get('status') == 'unsupported'
        else:
            passed = (model[2] == 0 and not model[1]
                      and actual.get('status') == row['expected_model']
                      and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program'
                      and base64.b64decode(actual.get('stdout', '')) == native[0]
                      and base64.b64decode(actual.get('stderr', '')) == native[1]
                      and actual.get('exit_status') == native[2])
        records.append({'case': name, 'pass': passed, 'control': control, 'native_exit': native[2],
                        'model_exit': model[2], 'model_status': actual.get('status'),
                        'source_sha256': sha(source), 'snapshot_sha256': sha(snapshot) if snapshot else None,
                        'raw_hashes': {name: sha(directory / name) for name in
                                       ('native.stdout', 'native.stderr', 'native.exit.json', 'model.stdout',
                                        'model.stderr', 'model.exit.json', 'commands.json')}})
        print(name, passed, flush=True)
    assert fingerprint == types.syntax_validation.implementation_fingerprint()
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    passed = all(record['pass'] for record in records)
    (out / 'report.json').write_text(json.dumps(
        {'passed': passed, 'fingerprint': fingerprint, 'inputs': hashes,
         'profile': profile, 'catalogue': catalogue,
         'agreements': sum(row['pass'] and not row['control'] for row in records),
         'controls': sum(row['pass'] and row['control'] for row in records), 'records': records}, indent=2) + '\n')
    print(out, passed, flush=True)
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--catalogue', action='store_true')
    selection.add_argument('--case', choices=['captured-static-saved-arguments'])
    options = parser.parse_args()
    raise SystemExit(0 if main(options.catalogue, options.case) else 1)
