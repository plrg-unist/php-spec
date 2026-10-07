#!/usr/bin/env python3
"""Independent original-source Fiber counterexamples; ordinary core PHP only."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT / '.tools/php/bin/php'
CASES = Path(__file__).with_name('fiber_review_cases.json')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--match', default='')
    parser.add_argument('--case', action='append')
    parser.add_argument('--native-report', action='append', type=Path, default=[])
    args = parser.parse_args()
    catalogue = json.loads(CASES.read_text())
    assert not args.case or set(args.case) <= {row['id'] for row in catalogue}, 'unknown Fiber review source'
    rows = [row for row in catalogue
            if args.match in row['id'] and (not args.case or row['id'] in args.case)
            and (args.case or row.get('run_by_default', True))]
    assert args.native_report or all(not row.get('native_held') for row in rows), 'held undefined-result native witness requires its preserved native report'
    assert rows, 'no Fiber review source selected'
    out = Path(tempfile.mkdtemp(prefix='fiber-review-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    previous = {}
    if args.native_report:
        assert not args.native_only, 'native reuse is for differential checks'
        identities = []
        for path in args.native_report:
            path = path.resolve()
            report = json.loads(path.read_text())
            assert (report['result'] == 'pass' or
                    (report['result'] == 'fail' and report['mode'] == 'native-only'))
            assert report['profile'] == profile
            identities.append(report['runtime'])
            for entry in report['results']:
                if entry['id'] not in {row['id'] for row in rows} or not entry['pass']:
                    continue
                assert entry['id'] not in previous, 'duplicate native source'
                previous[entry['id']] = (path, Path(report['raw']) / entry['id'])
        assert all(value == identities[0] for value in identities)
        identity = identities[0]
        assert identity['binary_sha256'] == digest(PHP), 'different native runtime'
    else:
        native_identity = subprocess.run([PHP, '-n', *flags, '-r',
            'echo json_encode(["version"=>PHP_VERSION,"sapi"=>PHP_SAPI,"int_size"=>PHP_INT_SIZE,"zts"=>PHP_ZTS,"extensions"=>get_loaded_extensions()]);'],
            cwd=ROOT, env=env, capture_output=True, timeout=30, check=True)
        identity = json.loads(native_identity.stdout)
    assert (identity['version'], identity['sapi'], identity['int_size'], identity['zts']) == ('8.5.10', 'cli', 8, False)
    identity['binary_sha256'] = digest(PHP)
    identity['source_commit'] = '34308a6666b2d489c509541ea9befea9e2b42348'
    watched = [CASES, Path(__file__), ROOT / 'tests/semantics/profile.json']
    if not args.native_only:
        changed = subprocess.check_output(['git', 'diff', '--name-only', 'ae0aa479eb5369c879c3b42c358a12aae0ec6c9f'], cwd=ROOT, text=True).splitlines()
        changed += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', 'spec/semantics'], cwd=ROOT, text=True).splitlines()
        watched += [ROOT / name for name in changed if name.endswith('.watsup')]
        watched += [ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics', ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    results = []
    for row in rows:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        assert digest(source) == row['source_sha256'], row['id']
        commands = [('native', [str(PHP), '-n', *flags, str(source)])]
        records = []
        if args.native_report:
            path, native_directory = previous[row['id']]
            assert (native_directory / 'source.php').read_bytes() == source.read_bytes(), 'different native source'
            native = dict(json.loads((native_directory / 'native.json').read_text()), reused_from=str(path))
            (directory / 'native.json').write_text(json.dumps(native, indent=2) + '\n')
            records.append(native)
            commands = []
        if not args.native_only:
            commands.append(('model', [str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '60']))
        for label, command in commands:
            try:
                result = subprocess.run(command, cwd=directory, env=env, capture_output=True, timeout=75)
                record = {'command': command, 'exit': result.returncode,
                          'stdout': base64.b64encode(result.stdout).decode(),
                          'stderr': base64.b64encode(result.stderr).decode()}
            except subprocess.TimeoutExpired as error:
                record = {'command': command, 'timeout': True,
                          'stdout': base64.b64encode(error.stdout or b'').decode(),
                          'stderr': base64.b64encode(error.stderr or b'').decode()}
            (directory / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
            records.append(record)
        native = records[0]
        passed = (native.get('exit') == row.get('native_exit', 0) and
                  base64.b64decode(native['stdout']) == row['native_stdout'].encode() and
                  (row.get('native_stderr') is None or base64.b64decode(native['stderr']) == row['native_stderr'].encode()))
        status = None
        if not args.native_only:
            model = records[1]
            try:
                observation = json.loads(base64.b64decode(model['stdout']))
            except (ValueError, UnicodeDecodeError):
                observation = {}
            status = observation.get('status')
            if row.get('expected_model') == 'unsupported':
                expected_stdout = base64.b64encode(row.get('unsupported_stdout', '').encode()).decode()
                passed = (passed and model.get('exit') == 1 and not base64.b64decode(model['stderr']) and
                          status == 'unsupported' and observation.get('reason') == row['unsupported_reason'] and
                          observation.get('events') == row.get('unsupported_events', []) and observation.get('stdout') == expected_stdout and
                          observation.get('stderr') == '' and 'exit_status' in observation and
                          observation['exit_status'] is None and 'diagnostic' in observation and
                          observation['diagnostic'] is None)
            else:
                passed = (passed and model.get('exit') == 0 and not base64.b64decode(model['stderr']) and
                          status == row.get('expected_model', 'normal') and
                          all(observation.get(key) == native[key] for key in ('stdout', 'stderr')) and
                          observation.get('exit_status') == native.get('exit'))
        results.append({'id': row['id'], 'pass': passed, 'native_exit': native.get('exit'), 'model_status': status,
                        'normal_agreement': passed and status == 'normal'})
        print(row['id'], passed, status or 'native', flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in watched}, 'review inputs changed during run'
    report = {'result': 'pass' if all(row['pass'] for row in results) else 'fail',
              'selection': [row['id'] for row in rows], 'mode': 'native-only' if args.native_only else 'source-differential',
              'revision': revision, 'inputs': before, 'runtime': identity, 'profile': profile,
              'compiler': {'spectec_source_commit': 'da36ac3c434cd291940293a63da64544307730a3',
                           'ocaml_switch': '5.1.0', 'semantic_mode': None if args.native_only else 'SL'},
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'budgets': {'steps': 100000, 'model_seconds': 60, 'process_seconds': 75},
              'results': results, 'normal_agreements': sum(row['normal_agreement'] for row in results), 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], flush=True)
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
