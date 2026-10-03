#!/usr/bin/env python3
"""Run the exact checked, algo-preflighted argument fixtures and retain raw exits."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import argument_introspection_current_protocol as current
import argument_introspection_protocol as arguments

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(report_path, case=None):
    preparation = json.loads(report_path.read_text())
    assert preparation['phase'] == 'parse/check/algo only; zero target/model execution'
    assert preparation['passed']
    group = preparation['group']
    assert group in {'current', 'retained'}
    cases = (current.CASES if group == 'current' else
             [case for case in arguments.CASES if case[0] != 'language-engine-defect-model-only'])
    expected = {case[0]: case[1] for case in cases}
    selected = preparation['records']
    assert len(selected) == len(expected) and {row['case'] for row in selected} == set(expected)
    if case:
        assert group == 'current' and case in expected
        selected = [row for row in selected if row['case'] == case]
        assert len(selected) == 1
        checks = next(candidate[3] for candidate in cases if candidate[0] == case)
        assert selected[0]['assertions'] == 2 + len(checks)
        expected = {case: expected[case]}
    inputs = dict(preparation['inputs'])
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs.update({str(runner): sha(runner), str(Path(__file__)): sha(Path(__file__)),
                   str(report_path): sha(report_path)})
    assert all(sha(Path(path)) == digest for path, digest in inputs.items())
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    out = Path(tempfile.mkdtemp(prefix='argument-prepared-' + group + '-', dir=ROOT / '.tools'))
    print(out, flush=True)
    records = []
    for row in selected:
        name = row['case']
        prepared = report_path.parent / name
        fixture = prepared / 'protocol.watsup'
        assert (prepared / 'source.php').read_bytes() == expected[name]
        for key, path in [('source_sha256', prepared / 'source.php'), ('fixture_sha256', fixture),
                          ('stdout_sha256', prepared / 'stdout.al'), ('stderr_sha256', prepared / 'stderr')]:
            assert sha(path) == row[key]
            inputs[str(path)] = row[key]
        assert row['passed'] and row['exit_status'] == 0 and not (prepared / 'stderr').read_bytes()
        assert b'\ndef $main : bool =\n' in (prepared / 'stdout.al').read_bytes()
        directory = out / name
        directory.mkdir()
        command = [str(runner), *map(str, modules), str(fixture)]
        (directory / 'command.json').write_text(json.dumps(command) + '\n')
        try:
            process = subprocess.run(command, capture_output=True, timeout=300)
            stdout, stderr, status = process.stdout, process.stderr, process.returncode
            exit_record = {'exit_status': status}
        except subprocess.TimeoutExpired as error:
            stdout, stderr, status = error.stdout or b'', error.stderr or b'', None
            exit_record = {'exit_status': None, 'exception': 'TimeoutExpired', 'timeout_seconds': 300}
        (directory / 'stdout').write_bytes(stdout)
        (directory / 'stderr').write_bytes(stderr)
        (directory / 'exit.json').write_text(json.dumps(exit_record) + '\n')
        passed = status == 0 and stdout == b'true\n' and not stderr
        records.append({'case': name, 'passed': passed, **exit_record,
                        'assertions': row['assertions'], 'source_sha256': row['source_sha256'],
                        'fixture_sha256': row['fixture_sha256'],
                        'raw_hashes': {name: sha(directory / name) for name in
                                       ('command.json', 'stdout', 'stderr', 'exit.json')}})
        print(name, passed, row['assertions'], flush=True)
    assert all(sha(Path(path)) == digest for path, digest in inputs.items())
    passed = all(row['passed'] for row in records)
    (out / 'report.json').write_text(json.dumps(
        {'passed': passed, 'group': group, 'preparation': str(report_path),
         'preparation_sha256': inputs[str(report_path)], 'inputs': inputs,
         'records': records, 'assertions': sum(row['assertions'] for row in records)}, indent=2) + '\n')
    print(out, passed, flush=True)
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    parser.add_argument('--case', choices=['captured-static-saved-arguments'])
    options = parser.parse_args()
    raise SystemExit(0 if main(options.report.resolve(), options.case) else 1)
