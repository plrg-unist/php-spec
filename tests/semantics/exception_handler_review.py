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
        except BaseException as error:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            if not isinstance(error, subprocess.TimeoutExpired):
                raise
            timed_out = True
    result = {'command': list(map(str, command)), 'exit': process.returncode, 'timeout': timed_out}
    (directory / (stem + '.process.json')).write_text(json.dumps(result) + '\n')
    return result


def run(match, native_only, native_reports):
    rows = [row for row in json.loads(CASES.read_text()) if match in row['id']]
    assert rows, 'no exception-handler source selected'
    out = Path(tempfile.mkdtemp(prefix='exceptions-review-', dir=ROOT / '.tools'))
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    runtime = ROOT / '.tools/php/bin/php'
    identities = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in (runtime, ROOT / '.tools/spectec/bin/p4spectec',
                               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so')}
    previous = {}
    for report_path in native_reports:
        report_path = report_path.resolve()
        evidence = json.loads(report_path.read_text())
        assert evidence['profile'] == profile, 'different native profile'
        for record in evidence['records']:
            assert record['id'] not in previous, 'duplicate native record'
            native = record.get('native', record)
            source = Path(native['command'][-1])
            stem = source.with_name('native') if source.name == 'source.php' else source.with_suffix('')
            previous[record['id']] = (native, source, stem, report_path)
    print(out, flush=True)
    results = []
    for row in rows:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        if native_reports:
            native, source, stem, report_path = previous[row['id']]
            assert source.read_bytes() == row['source'].encode(), 'native source differs'
            native = dict(native, reused_from=str(report_path))
            for suffix in ('stdout', 'stderr'):
                (directory / ('native.' + suffix)).write_bytes(stem.with_suffix('.' + suffix).read_bytes())
        else:
            source.write_text(row['source'])
            native = recorded([runtime, '-n', *flags, source], directory, 'native', environment, 30)
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        nout = (directory / 'native.stdout').read_bytes()
        nerr = (directory / 'native.stderr').read_bytes()
        passed = (not native.get('timeout', False) and native['exit'] == row['exit']
                  and nout == row['stdout'].encode()
                  and nerr == row['stderr'].replace('{file}', str(source)).encode())
        result = {'id': row['id'], 'native': native, 'passed': passed}
        if passed and not native_only:
            model = recorded([ROOT / 'bin/php-semantics', source, '--steps', '100000', '--timeout', '60'],
                             directory, 'model', environment, 75)
            try:
                actual = json.loads((directory / 'model.stdout').read_bytes())
            except ValueError:
                actual = {'runner_error': 'invalid model JSON'}
            if not isinstance(actual, dict):
                actual = {'runner_error': 'model result is not an object'}
            passed = (not model['timeout'] and model['exit'] == 0
                      and not (directory / 'model.stderr').read_bytes()
                      and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program'
                      and actual.get('status') == row['status'] and actual.get('exit_status') == native['exit']
                      and base64.b64decode(actual['stdout']) == nout and base64.b64decode(actual['stderr']) == nerr)
            result.update(model=model, observation=actual, passed=passed)
        results.append(result)
        print(row['id'], passed, flush=True)
        if not passed:
            break
    report = {'revision': revision, 'identities': identities,
              'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
              'scope': 'native only' if native_only else 'original-source differential tuples',
              'selection': [row['id'] for row in rows], 'records': results,
              'passed': len(results) == len(rows) and all(result['passed'] for result in results)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--match', default='')
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--native-report', type=Path, action='append', default=[],
                        help='reuse unchanged native source and raw streams from a report or manifest')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match, args.native_only, args.native_report) else 1)
