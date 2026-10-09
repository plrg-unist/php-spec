#!/usr/bin/env python3
"""Compare retained original source tuples against the checked CLI."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import signal
import subprocess
import tempfile

import static_types as types

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / 'tests/semantics/method_runtime_cases.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned_members(pgid):
    members = []
    for path in Path('/proc').iterdir():
        if not path.name.isdigit():
            continue
        try:
            if int((path / 'stat').read_text().rsplit(')', 1)[1].split()[2]) == pgid:
                members.append(int(path.name))
        except (OSError, ValueError):
            pass
    return members


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
        if 'startup_ini' in row:
            startup = directory / 'startup-ini.json'
            startup.write_text(json.dumps(row['startup_ini']) + '\n')
            command += ['--startup-ini', str(startup)]
        entries = []
        for child in row.get('files', []):
            assert Path(child['name']).name == child['name'], 'invalid child filename'
            path = directory / child['name']
            path.write_bytes(child['source'].encode())
            assert sha(path) == child['source_sha256'], child['name']
            encoded = base64.b64encode(os.fsencode(path)).decode()
            entries.append({'caller': base64.b64encode(os.fsencode(source)).decode(),
                            'requested': encoded, 'status': 'opened',
                            'resolved': encoded, 'opened': encoded,
                            'source': base64.b64encode(path.read_bytes()).decode()})
        if entries:
            snapshot = directory / 'snapshot.json'
            snapshot.write_text(json.dumps({'version': 1,
                'main': base64.b64encode(os.fsencode(source)).decode(),
                'cwd': base64.b64encode(os.fsencode(directory)).decode(),
                'include_path': base64.b64encode(b'.:').decode(), 'entries': entries}) + '\n')
            command += ['--file-snapshot', str(snapshot)]
        stdout_path, stderr_path = directory / 'runner.stdout', directory / 'runner.stderr'
        producer = {'supplied_argv': command, 'supplied_cwd': str(directory),
                    'supplied_environment': environment, 'host_timeout_seconds': 55,
                    'observed_exit': None, 'cleanup_exit': None, 'status': 'prepared'}
        command_path = directory / 'runner.command.json'
        command_path.write_text(json.dumps(producer, indent=2) + '\n')
        with stdout_path.open('wb') as stdout_stream, stderr_path.open('wb') as stderr_stream:
            process = None
            try:
                process = subprocess.Popen(command, cwd=directory, env=environment,
                    stdout=stdout_stream, stderr=stderr_stream, start_new_session=True)
                producer.update(popen_args=process.args, pid=process.pid,
                                owned_pgid=process.pid, status='running')
                command_path.write_text(json.dumps(producer, indent=2) + '\n')
                producer['observed_exit'] = process.wait(timeout=55)
            except subprocess.TimeoutExpired:
                producer['timeout_expired'] = True
            finally:
                if process is not None:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    try:
                        producer['cleanup_exit'] = process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        producer['cleanup_timeout'] = True
                    producer['owned_group_after'] = owned_members(process.pid)
                producer['status'] = 'closed'
                command_path.write_text(json.dumps(producer, indent=2) + '\n')
        status = producer['observed_exit']
        stdout, stderr = stdout_path.read_bytes(), stderr_path.read_bytes()
        (directory / 'runner.status.json').write_text(json.dumps({'exit_status': status}) + '\n')
        try:
            actual = json.loads(stdout)
        except json.JSONDecodeError:
            actual = {'status': 'runner_failure'}
        passed = (status == 0 and producer['cleanup_exit'] == 0
                  and producer.get('owned_group_after') == [] and not stderr
                  and actual.get('status') == row['status'])
        passed = passed and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program' and actual.get('reason') is None
        passed = passed and actual.get('exit_status') == row['exit_status']
        stderr = base64.b64decode(row['stderr_template_base64']).replace(
            b'{FILE}', str(source).encode())
        for child in row.get('files', []):
            stderr = stderr.replace(b'{FILE:' + child['name'].encode() + b'}',
                                    os.fsencode(directory / child['name']))
        expected_stdout = row['stdout_base64']
        if 'stdout_template_base64' in row:
            expected_stdout = base64.b64encode(base64.b64decode(row['stdout_template_base64']).replace(
                b'{FILE}', str(source).encode())).decode()
        passed = passed and actual.get('stdout') == expected_stdout
        passed = passed and actual.get('stderr') == base64.b64encode(stderr).decode()
        native_profile = row.get('native_profile', shared_profile or {})
        if isinstance(shared_profile, dict) and isinstance(native_profile, dict):
            native_profile = dict(shared_profile, **native_profile)
        records.append({'id': row['id'], 'pass': passed,
                        'native_group': row['native_group'],
                        'native_raw_sha256': row['native_raw_sha256'],
                        'native_profile': native_profile,
                        'source_sha256': row['source_sha256'],
                        'command_record': str(command_path),
                        'runner_exit_status': status,
                        'actual': actual})
        print(row['id'], passed, actual.get('status'), flush=True)
        if not passed:
            break
    stable = before == types.syntax_validation.implementation_fingerprint() and all(
        sha(ROOT / name) == digest for name, digest in direct.items())
    report = {'result': 'pass' if stable and len(records) == len(selected)
              and all(row['pass'] for row in records) else 'fail',
              'selection': match, 'selected_cases': len(selected),
              'catalogue_cases': len(cases),
              'completed_cases': len(records),
              'conditional_unrun': [row['id'] for row in selected[len(records):]],
              'fingerprint': before, 'direct_inputs': direct, 'inputs_stable': stable,
              'raw': str(out), 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    parser.add_argument('--catalogue', type=Path, default=DEFAULT_CASES)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match, args.catalogue) else 1)
