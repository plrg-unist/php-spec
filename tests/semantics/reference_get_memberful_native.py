"""Frozen native-first and unchanged-model probes for memberful reference Get."""
import argparse
import base64
import hashlib
import json
import subprocess
from pathlib import Path

import grandchild_reference_get_hook_protocol as old

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'reference_get_memberful_cases.json'
EXPECTATIONS = HERE / 'reference_get_memberful_expectations.json'
FROZEN = 'a8959d9c92a7ad362db8082355db38af7adae69efdb6a52446cc944834dc873e'
OUT = ROOT / '.tools/class139-probes'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_paths():
    assert sha(CATALOGUE) == FROZEN
    php = ROOT / '.tools/php/bin/php'
    profile = HERE / 'profile.json'
    flags = [part for key, value in json.loads(profile.read_text()).items()
             for part in ('-d', key + '=' + value)]
    return php, profile, flags, json.loads(CATALOGUE.read_text())['cases']


def source_path(case):
    path = OUT / 'sources' / (case['id'] + '.php')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(case['source'].encode())
    assert sha(path) == case['source_sha256']
    return path


def native():
    php, profile, flags, cases = input_paths()
    assert not EXPECTATIONS.exists(), 'preserve native expectations after freeze'
    rows = {}
    for case in cases:
        path = source_path(case)
        result = old.base.run([str(php), '-n', *flags, str(path)],
                              OUT / ('native-' + case['id']), 25)
        rows[case['id']] = {
            'source_sha256': sha(path), 'exit_status': result.returncode,
            'stdout_base64': base64.b64encode(result.stdout).decode(),
            'stderr_base64': base64.b64encode(result.stderr).decode(),
        }
        print(case['id'], result.returncode, result.stdout, result.stderr, flush=True)
    report = {
        'catalogue_sha256': FROZEN, 'oracle_sha256': sha(php),
        'native_profile_sha256': sha(profile), 'cases': rows,
    }
    EXPECTATIONS.write_text(json.dumps(report, indent=2) + '\n')
    (OUT / 'native-first.json').write_text(json.dumps(report, indent=2) + '\n')
    print('native expectations', sha(EXPECTATIONS), flush=True)


def baseline():
    php, profile, flags, cases = input_paths()
    expected = json.loads(EXPECTATIONS.read_text())
    assert expected['catalogue_sha256'] == FROZEN
    assert expected['oracle_sha256'] == sha(php)
    assert expected['native_profile_sha256'] == sha(profile)
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip() == json.loads(CATALOGUE.read_text())['baseline_revision']
    assert not subprocess.check_output(['git', 'diff', '--', 'spec/semantics'], cwd=ROOT)
    rows = {}
    for case in cases:
        path = source_path(case)
        result = old.base.run([str(ROOT / 'bin/php-semantics'), str(path),
                               '--steps', '100000', '--timeout', '75'],
                              OUT / ('baseline-' + case['id']), 90)
        outcome = json.loads(result.stdout)
        rows[case['id']] = {
            'source_sha256': sha(path), 'exit_status': result.returncode,
            'frontend': outcome.get('frontend'), 'checked': outcome.get('checked'),
            'status': outcome['status'], 'reason': outcome.get('reason'),
            'stdout': outcome.get('stdout'), 'stderr': outcome.get('stderr'),
            'diagnostic': outcome.get('diagnostic'),
        }
        print(case['id'], rows[case['id']], flush=True)
    report = {
        'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'catalogue_sha256': FROZEN, 'expectations_sha256': sha(EXPECTATIONS),
        'semantic_sha256': sha(ROOT / 'spec/semantics/382-backed-get-hooks.watsup'),
        'adapter_sha256': sha(ROOT / '_build/default/adapter/main.exe'),
        'cases': rows,
    }
    (OUT / 'unchanged-baseline.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['native', 'baseline'])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    (native if args.phase == 'native' else baseline)()
