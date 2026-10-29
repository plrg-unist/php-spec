#!/usr/bin/env python3
"""Capture pinned PHP outputs for frozen early Deprecated callback sources."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import deprecated_api_cases as cases
import deprecated_api_review_cases as reviewed
import deprecated_exception_cases as exceptions
from error_handler_run import ENV, recorded


ROOT = Path(__file__).resolve().parents[2]
CASES = {**cases.CASES, **reviewed.CASES, **exceptions.CASES}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--case', choices=tuple(CASES))
    parser.add_argument('--group', choices=('attr03', 'attr04'), default='attr03')
    args = parser.parse_args()
    affinity = sorted(os.sched_getaffinity(0))
    assert len(affinity) == 1 and affinity[0] in range(1, 6)
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    output = args.output.resolve()
    output.mkdir(parents=True)
    watched = [Path(__file__), Path(cases.__file__), Path(reviewed.__file__), Path(exceptions.__file__), ROOT / '.tools/php/bin/php',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py']
    inputs = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [item for key, value in profile.items() for item in ('-d', key + '=' + value)]
    selected = ((args.case,) if args.case else
                (tuple(exceptions.CASES) if args.group == 'attr04' else tuple(cases.CASES) + tuple(reviewed.CASES)))
    rows = []
    for name in selected:
        folder = output / name
        folder.mkdir()
        source = folder / 'source.php'
        source.write_bytes(CASES[name])
        process = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], folder / 'native', 30)
        stdout = (folder / 'native.stdout').read_bytes()
        stderr = (folder / 'native.stderr').read_bytes()
        expected = (cases if name in cases.CASES else
                    reviewed if name in reviewed.CASES else exceptions)
        expected_stdout = expected.EXPECTED_STDOUT[name]
        expected_stderr = expected.expected_stderr(name, source)
        passed = (process['exit'] == expected.EXIT_CODES[name] and not process['timeout']
                  and process['interruption'] is None and not process['group_after']
                  and stdout == expected_stdout and stderr == expected_stderr)
        rows.append({'id': name, 'source_sha256': digest(source), 'native': process,
                     'stdout_b64': base64.b64encode(stdout).decode(),
                     'stderr_b64': base64.b64encode(stderr).decode(),
                     'expected_stdout_b64': base64.b64encode(expected_stdout).decode(),
                     'expected_stderr_b64': base64.b64encode(expected_stderr).decode(),
                     'passed': passed, 'agreement_credit': 0})
        print(name, passed, flush=True)
    assert inputs == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    report = {'revision': revision, 'inputs': inputs, 'profile': profile,
              'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
              'affinity': affinity, 'selection': selected,
              'rows': rows, 'passed': all(row['passed'] for row in rows)}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
