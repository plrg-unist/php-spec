#!/usr/bin/env python3
"""First-class static Fiber API originals, serial native/model checks."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from exception_handler_review import recorded

CASES = Path(__file__).with_name('fiber_static_api_cases.json')
PREFIX = 'fiber-static-api-source-'
IMPLEMENTATION = Path(__file__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--native-report', type=Path, action='append', default=[])
    args = parser.parse_args()
    cases = json.loads(CASES.read_bytes())
    assert set(args.case) <= {row['id'] for row in cases}
    cases = [row for row in cases if not args.case or row['id'] in args.case]
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    runtime = {'version': '8.5.10', 'sapi': 'cli', 'int_size': 8, 'zts': False,
               'source_commit': '34308a6666b2d489c509541ea9befea9e2b42348',
               'binary_sha256': digest(ROOT / '.tools/php/bin/php')}
    assert runtime['binary_sha256'] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    native_previous = {}
    for path in args.native_report:
        path = path.resolve()
        report = json.loads(path.read_bytes())
        assert report['profile'] == profile and report['mode'] == 'native-only'
        assert report.get('runtime_sha256', report.get('runtime', {}).get('binary_sha256')) == runtime['binary_sha256']
        for row in report.get('rows', report.get('results', [])):
            if row['id'] not in {case['id'] for case in cases} or not row.get('passed', row.get('pass')):
                continue
            assert row['id'] not in native_previous
            directory = Path(report.get('raw', path.parent)) / row['id']
            if 'actual_stdout' in row:
                native = dict(row['process'], stdout=row['actual_stdout'], stderr=row['actual_stderr'])
            else:
                native = json.loads((directory / 'native.json').read_bytes())
            native_previous[row['id']] = (path, directory / 'source.php', native)
    if args.native_report:
        assert set(native_previous) == {row['id'] for row in cases}
    out = Path(tempfile.mkdtemp(prefix=PREFIX, dir=ROOT / '.tools'))
    print(out, flush=True)
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, text=True).strip()
    revision = git('rev-parse', 'HEAD')
    watched = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    watched += [ROOT / name for name in ('spec/semantics/modules.json', 'bin/php-semantics',
                '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
                '.tools/php/bin/php', '.tools/php-file.so', 'tests/semantics/profile.json',
                'tests/semantics/exception_handler_review.py')]
    watched += [IMPLEMENTATION, Path(__file__), CASES]
    watched += [source for _, source, _ in native_previous.values()]
    before = {str(path): digest(path) for path in watched}
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    records = []
    for row in cases:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        assert digest(source) == row['source_sha256']
        if args.native_report:
            path, original, native = native_previous[row['id']]
            assert original.read_bytes() == source.read_bytes()
            source = original
            native = dict(native, reused_from=str(path))
            nout, nerr = base64.b64decode(native['stdout']), base64.b64decode(native['stderr'])
        else:
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], directory, 'native', env, 75)
            nout, nerr = (directory / 'native.stdout').read_bytes(), (directory / 'native.stderr').read_bytes()
        expected_stderr = row['native_stderr'].replace('{source}', str(source)).encode()
        passed = (native.get('exit') == row['native_exit'] and not native.get('timeout')
                  and nout == row['native_stdout'].encode() and nerr == expected_stderr)
        record = {'id': row['id'], 'source_sha256': row['source_sha256'], 'native': native, 'passed': False}
        if passed:
            model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '60'], directory, 'model', env, 75)
            try:
                outcome = json.loads((directory / 'model.stdout').read_bytes())
            except ValueError:
                outcome = {}
            passed = (not model['timeout'] and (directory / 'model.stderr').read_bytes() == b''
                      and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program')
            if row.get('expected_model') == 'unsupported':
                passed = (passed and model['exit'] == 1 and outcome.get('status') == 'unsupported'
                          and outcome.get('exit_status') is None and outcome.get('diagnostic') is None
                          and outcome.get('reason') == row['unsupported_reason']
                          and outcome.get('events') == row.get('unsupported_events', [])
                          and outcome.get('stdout') == base64.b64encode(row.get('unsupported_stdout', '').encode()).decode()
                          and outcome.get('stderr') == '')
            else:
                passed = (passed and model['exit'] == 0 and outcome.get('status') == row.get('expected_model', 'normal')
                          and outcome.get('exit_status') == row['native_exit'] and outcome.get('reason') is None
                          and outcome.get('stdout') == base64.b64encode(nout).decode()
                          and outcome.get('stderr') == base64.b64encode(nerr).decode())
                if row.get('expected_model') == 'php_error':
                    passed = passed and row['native_exit'] == 255 and outcome.get('diagnostic') is not None
            record.update(model=model, outcome=outcome)
        record['passed'] = passed
        records.append(record)
        print(row['id'], passed, record.get('outcome', {}).get('status'), flush=True)
        if not passed:
            break
    stable = before == {str(path): digest(path) for path in watched}
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable,
              'head_stable': revision == git('rev-parse', 'HEAD'), 'selection': [row['id'] for row in cases],
              'records': records, 'normal_agreements': sum(row['passed'] and row.get('outcome', {}).get('status') == 'normal' for row in records),
              'php_error_agreements': sum(row['passed'] and row.get('outcome', {}).get('status') == 'php_error' for row in records),
              'runtime': runtime, 'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1},
              'compiler': {'mode': 'SL', 'cache': False, 'determinism_checks': True,
                           'spectec_commit': 'da36ac3c434cd291940293a63da64544307730a3', 'ocaml': '5.1.0'},
              'budgets': {'steps': 100000, 'model_seconds': 60, 'process_seconds': 75},
              'passed': stable and len(records) == len(cases) and all(row['passed'] for row in records)}
    report['passed'] = report['passed'] and report['head_stable']
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
