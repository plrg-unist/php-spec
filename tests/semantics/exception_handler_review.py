#!/usr/bin/env python3
"""Independent exact source tuples for exception-handler registration/dispatch."""
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
CASES = Path(__file__).with_name('exception_handler_review_cases.json')


def recorded(command, directory, stem, environment, cap):
    with (directory / (stem + '.stdout')).open('wb') as stdout, (directory / (stem + '.stderr')).open('wb') as stderr:
        process = subprocess.Popen(command, cwd=directory, env=environment,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        timed_out = False
        try:
            process.wait(timeout=cap)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    result = {'command': list(map(str, command)), 'exit': process.returncode, 'timeout': timed_out}
    (directory / (stem + '.process.json')).write_text(json.dumps(result) + '\n')
    return result


def run(match, native_only):
    rows = [row for row in json.loads(CASES.read_text()) if match in row['id']]
    assert rows, 'no exception-handler source selected'
    out = Path(tempfile.mkdtemp(prefix='exceptions-review-', dir=ROOT / '.tools'))
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    runtime = ROOT / '.tools/php/bin/php'
    print(out, flush=True)
    results = []
    for row in rows:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(row['source'])
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        native = recorded([runtime, '-n', *flags, source], directory, 'native', environment, 30)
        nout = (directory / 'native.stdout').read_bytes()
        nerr = (directory / 'native.stderr').read_bytes()
        passed = (not native['timeout'] and native['exit'] == row['exit']
                  and nout == row['stdout'].encode()
                  and nerr == row['stderr'].replace('{file}', str(source)).encode())
        result = {'id': row['id'], 'native': native, 'passed': passed}
        if passed and not native_only:
            model = recorded([ROOT / 'bin/php-semantics', source, '--steps', '100000', '--timeout', '60'],
                             directory, 'model', environment, 75)
            actual = json.loads((directory / 'model.stdout').read_bytes())
            passed = (not model['timeout'] and model['exit'] == 0
                      and not (directory / 'model.stderr').read_bytes()
                      and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program'
                      and actual.get('status') == row['status'] and actual.get('exit_status') == native['exit']
                      and base64.b64decode(actual['stdout']) == nout and base64.b64decode(actual['stderr']) == nerr)
            result.update(model=model, observation=actual, passed=passed)
        results.append(result)
        print(row['id'], passed, flush=True)
    report = {'revision': revision, 'runtime_sha256': hashlib.sha256(runtime.read_bytes()).hexdigest(),
              'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
              'scope': 'native only' if native_only else 'original-source differential tuples',
              'selection': [row['id'] for row in rows], 'records': results,
              'passed': all(result['passed'] for result in results)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--match', default='')
    parser.add_argument('--native-only', action='store_true')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match, args.native_only) else 1)
