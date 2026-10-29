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
from error_handler_run import ENV, recorded


ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--case', choices=tuple(cases.CASES))
    args = parser.parse_args()
    assert sorted(os.sched_getaffinity(0)) == [4]
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    output = args.output.resolve()
    output.mkdir(parents=True)
    watched = [Path(__file__), Path(cases.__file__), ROOT / '.tools/php/bin/php',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py']
    inputs = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [item for key, value in profile.items() for item in ('-d', key + '=' + value)]
    selected = (args.case,) if args.case else tuple(cases.CASES)
    rows = []
    for name in selected:
        folder = output / name
        folder.mkdir()
        source = folder / 'source.php'
        source.write_bytes(cases.CASES[name])
        process = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], folder / 'native', 30)
        stdout = (folder / 'native.stdout').read_bytes()
        stderr = (folder / 'native.stderr').read_bytes()
        expected_stdout = cases.EXPECTED_STDOUT[name]
        expected_stderr = cases.expected_stderr(name, os.fsencode(source))
        passed = (process['exit'] == cases.EXIT_CODES[name] and not process['timeout']
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
              'affinity': sorted(os.sched_getaffinity(0)), 'selection': selected,
              'rows': rows, 'passed': all(row['passed'] for row in rows)}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
