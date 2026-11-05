#!/usr/bin/env python3
"""Exact PHP 8.5.10 source comparison for named constructor factories."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_factory_cases.json'
PROFILE = ROOT / 'tests/semantics/profile.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, timeout):
    process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True,
                               env=dict(os.environ, LC_ALL='C', TZ='UTC'))
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        timed_out = True
    return {'command': command, 'exit_code': process.returncode,
            'stdout_base64': base64.b64encode(stdout).decode(),
            'stderr_base64': base64.b64encode(stderr).decode(), 'timeout': timed_out}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', help='Run only this case ID; repeat as needed')
    args = parser.parse_args()
    catalogue = json.loads(CATALOGUE.read_text())
    rows = catalogue['cases']
    if args.case:
        assert set(args.case) <= {row['id'] for row in rows}
        rows = [row for row in rows if row['id'] in args.case]
    assert catalogue['native_profile'] == json.loads(PROFILE.read_text())
    flags = [item for key, value in catalogue['native_profile'].items()
             for item in ('-d', key + '=' + value)]
    php = ROOT / '.tools/php/bin/php'
    adapter = ROOT / '_build/default/adapter/main.exe'
    watched = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched += [ROOT / 'spec/semantics/modules.json', CATALOGUE, PROFILE,
                Path(__file__), php, adapter, ROOT / '.tools/php-file.so']
    before = {str(path): digest(path) for path in watched}
    raw = Path(tempfile.mkdtemp(prefix='class179-source-', dir=ROOT / '.tools'))
    results = []
    for row in rows:
        source = row['source'].encode()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        filename = raw / (row['id'] + '.php')
        filename.write_bytes(source)
        native = run([str(php), '-n', *flags, str(filename)], raw, 30)
        model = run([str(ROOT / 'bin/php-semantics'), str(filename),
                     '--steps', '100000', '--timeout', '60'], raw, 70)
        expected_out = base64.b64decode(row['stdout_template_base64']).replace(b'{FILE}', os.fsencode(filename))
        expected_err = base64.b64decode(row['stderr_template_base64']).replace(b'{FILE}', os.fsencode(filename))
        try:
            outcome = json.loads(base64.b64decode(model['stdout_base64']))
        except (json.JSONDecodeError, UnicodeDecodeError):
            outcome = {}
        native_exact = (not native['timeout'] and native['exit_code'] == row['exit_status']
                        and base64.b64decode(native['stdout_base64']) == expected_out
                        and base64.b64decode(native['stderr_base64']) == expected_err)
        model_exact = (not model['timeout'] and model['exit_code'] == 0
                       and outcome.get('status') == row['status']
                       and outcome.get('exit_status') == row['exit_status']
                       and base64.b64decode(outcome.get('stdout', '')) == expected_out
                       and base64.b64decode(outcome.get('stderr', '')) == expected_err)
        result = {'id': row['id'], 'source_sha256': row['source_sha256'],
                  'native_exact': native_exact, 'model_exact': model_exact,
                  'model_status': outcome.get('status'), 'model_reason': outcome.get('reason')}
        results.append(result)
        (raw / (row['id'] + '.native.json')).write_text(json.dumps(native, indent=2) + '\n')
        (raw / (row['id'] + '.model.json')).write_text(json.dumps(model, indent=2) + '\n')
        print(row['id'], 'PASS' if native_exact and model_exact else 'FAIL', flush=True)
    after = {str(path): digest(path) for path in watched}
    report = {'selection': [row['id'] for row in rows], 'target': 'PHP 8.5.10 CLI/NTS/64-bit',
              'profile': catalogue['native_profile'], 'inputs_before': before,
              'inputs_after': after, 'stable': before == after, 'results': results,
              'passed': before == after and all(r['native_exact'] and r['model_exact'] for r in results),
              'raw': str(raw)}
    (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(raw / 'report.json')
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
