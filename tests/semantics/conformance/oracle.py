#!/usr/bin/env python3
"""Validate independently authored targets against the pinned oracle only."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PHP = ROOT / '.tools/php/bin/php'
PROFILE = ROOT / 'tests/semantics/profile.json'
CATALOG = HERE / 'cases.json'


def main():
    catalog = json.loads(CATALOG.read_text())
    profile = json.loads(PROFILE.read_text())
    watched = [PHP, PROFILE, CATALOG, Path(__file__)] + [ROOT / c['file'] for c in catalog['cases']]
    def fingerprints():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = fingerprints()
    flags = [x for k, v in profile.items() for x in ('-d', k + '=' + v)]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    identity = subprocess.run([str(PHP), '-n', *flags, '-r',
        'echo json_encode(["version"=>PHP_VERSION,"sapi"=>PHP_SAPI,"int_size"=>PHP_INT_SIZE,"zts"=>PHP_ZTS,"extensions"=>get_loaded_extensions()]);'],
        capture_output=True, env=environment, timeout=5, check=True)
    target = json.loads(identity.stdout)
    assert target['version'] == '8.5.10' and target['sapi'] == 'cli'
    assert target['int_size'] == 8 and target['zts'] is False
    results = []
    for case in catalog['cases']:
        path = ROOT / case['file']
        run = subprocess.run([str(PHP), '-n', *flags, str(path)], capture_output=True,
                             cwd=path.parent, env=environment, timeout=5)
        expected = (case['expected_stdout'].encode(),
                    case['expected_stderr'].replace('{FILE}', str(path)).encode(),
                    case['expected_exit_status'])
        actual = (run.stdout, run.stderr, run.returncode)
        assert actual == expected, (case['id'], actual, expected)
        results.append({'id': case['id'], 'source_sha256': before[case['file']],
                        'file': str(path), 'cwd': str(path.parent),
                        'stdout': base64.b64encode(run.stdout).decode(),
                        'stderr': base64.b64encode(run.stderr).decode(),
                        'exit_status': run.returncode, 'expected_match': True})
    assert fingerprints() == before, 'oracle witness inputs changed during run'
    report = {'scope': 'oracle-only conformance targets; no semantic evaluator was run',
              'source_pin': '34308a6666b2d489c509541ea9befea9e2b42348',
              'target': target, 'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'timeout_seconds': 5, 'fingerprints': before, 'results': results}
    (ROOT / 'coverage/semantics/conformance-oracle.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'{len(results)} oracle-only source targets matched; semantic coverage remains pending.')


if __name__ == '__main__':
    main()
