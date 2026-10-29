"""Compare frozen dynamic-only clone sources with the pinned PHP observations."""
import argparse
import base64
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import error_handler_run as recorder

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu', type=int)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    affinity = sorted(os.sched_getaffinity(0))
    if args.cpu is not None:
        assert affinity == [args.cpu]
    recorder.ROOT = ROOT
    expectations = HERE / 'dynamic_only_cached_clone_expectations.json'
    expected = json.loads(expectations.read_text())
    php = ROOT / '.tools/php/bin/php'
    profile = HERE / 'profile.json'
    assert sha(php) == expected['oracle_sha256']
    assert sha(profile) == expected['native_profile_sha256']
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_text())]
    watched = [Path(__file__).resolve(), expectations, php, profile, manifest,
               ROOT / 'bin/php-semantics', ROOT / '_build/default/adapter/main.exe', *modules]
    catalogues = {}
    for group, item in expected['catalogues'].items():
        path = HERE / item['file']
        assert sha(path) == item['sha256']
        catalogues[group] = json.loads(path.read_text())
        watched.append(path)
    watched = list(dict.fromkeys(watched))
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    assert before['spec/semantics/150-clone-runtime.watsup'] == '4944e488aeaff570e92ded6ed27dc361b2259be2b9d268f2184fbcef186cecba'
    assert before['spec/semantics/261-object-casts.watsup'] == 'ee046c71bf74c8b0061d34f29adfdb52362e11cfcf7e03502e2aa7ed90fa98f5'
    keys = [group + '/' + case['id'] for group, data in catalogues.items() for case in data['cases']]
    assert set(keys) == set(expected['cases']) and len(keys) == 14
    if args.case:
        assert len(args.case) == len(set(args.case)) and set(args.case) <= set(keys)
        keys = [key for key in keys if key in args.case]
    out = Path(tempfile.mkdtemp(prefix='class141-sources-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'inputs_before': before, 'affinity': affinity, 'selection': keys, 'cases': {}, 'complete': False, 'passed': False}
    try:
        for key in keys:
            group, case_id = key.split('/', 1)
            case = next(item for item in catalogues[group]['cases'] if item['id'] == case_id)
            observation = expected['cases'][key]
            assert case['source_sha256'] == observation['source_sha256']
            source = out / (group + '-' + case_id + '.php')
            source.write_bytes(case['source'].encode())
            assert sha(source) == case['source_sha256']
            process = recorder.recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '75'],
                                        out / (group + '-' + case_id), 90)
            raw_stdout = (out / (group + '-' + case_id + '.stdout')).read_bytes()
            raw_stderr = (out / (group + '-' + case_id + '.stderr')).read_bytes()
            try:
                outcome = json.loads(raw_stdout)
                actual = (outcome.get('exit_status'), base64.b64decode(outcome.get('stdout', '')),
                          base64.b64decode(outcome.get('stderr', '')))
            except (ValueError, KeyError):
                outcome = {}
                actual = (None, b'', b'')
            native = (observation['exit_status'], base64.b64decode(observation['stdout_base64']),
                      base64.b64decode(observation['stderr_base64']))
            passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and
                      raw_stderr == b'' and outcome.get('status') == 'normal' and
                      outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program' and actual == native)
            report['cases'][key] = {'source_sha256': sha(source), 'changed_credit': observation['changed_credit'],
                                    'process': process, 'raw_stdout_sha256': sha(out / (group + '-' + case_id + '.stdout')),
                                    'raw_stderr_sha256': sha(out / (group + '-' + case_id + '.stderr')),
                                    'status': outcome.get('status'), 'frontend': outcome.get('frontend'),
                                    'checked': outcome.get('checked'), 'passed': passed}
            (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(key, 'PASS' if passed else 'FAIL', outcome.get('status'), flush=True)
            if not passed:
                break
        report['complete'] = len(report['cases']) == len(keys)
        report['passed'] = report['complete'] and all(row['passed'] for row in report['cases'].values())
    finally:
        report['inputs_after'] = {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_after'] == before
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
