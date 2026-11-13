#!/usr/bin/env python3
"""Run multiple-CV producer originals and both actual Notice-state fixtures serially."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import fiber_static_api_sources as source
from multi_cv_producer_reference_notice_review_cases import CASES, HASHES
from scalar_return_producer_cv_reference_notice_run import native_record, recorded

ROOT = Path(__file__).resolve().parents[2]


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    tests = ROOT / 'tests/semantics'
    author_cases = tests / 'multi_cv_producer_reference_notice_cases.json'
    peer_cases = tests / 'multi_cv_producer_reference_notice_review_cases.py'
    expected_path = tests / 'multi_cv_producer_reference_notice_review_expected.json'
    author_state = tests / 'multi_cv_producer_reference_notice_state.py'
    peer_state = tests / 'multi_cv_producer_reference_notice_review_state.py'
    watched = [Path(__file__), author_cases, peer_cases, expected_path, author_state, peer_state,
        tests / 'scalar_return_producer_cv_reference_notice_run.py', tests / 'error_handler_run.py']
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = fingerprints()
    directory = Path(tempfile.mkdtemp(prefix='multi-cv-producer-reference-run-', dir=ROOT / '.tools'))
    print(directory, flush=True)
    expected = json.loads(expected_path.read_bytes())
    assert [row['id'] for row in expected] == list(CASES)
    peer = []
    for row in expected:
        name = row['id']
        assert row['source_sha256'] == HASHES[name]
        peer.append(dict(row, source=CASES[name].decode()))
    cases = json.loads(author_cases.read_bytes()) + peer
    assert len(cases) == len({row['id'] for row in cases}) == 8
    catalogue = directory / 'cases.json'
    catalogue.write_text(json.dumps(cases, indent=2) + '\n')
    source.CASES, source.IMPLEMENTATION = catalogue, Path(__file__)
    source.PREFIX = str(directory / 'sources-')
    source.MODEL_SECONDS, source.PROCESS_SECONDS = 180, 195
    source.recorded = recorded
    if not source.main():
        return False
    source_path, = directory.glob('sources-*/report.json')
    report = json.loads(source_path.read_bytes())
    assert report['normal_agreements'] == len(report['records']) == 8
    assert report['passed'] and report['inputs_stable'] and report['head_stable']
    assert before == fingerprints()
    runtime = report['runtime']['binary_sha256']
    native = [native_record(row) for row in report['records']]
    author_native = directory / 'author-native.json'
    author_native.write_text(json.dumps(dict(mode='native-first', passed=True,
        inputs_stable=report['inputs_stable'], head_stable=report['head_stable'],
        runtime_sha256=runtime, profile=report['profile'],
        derived_from=str(source_path), records=native[:3]), indent=2) + '\n')
    peer_native = directory / 'peer-native.json'
    peer_records = []
    for row, wanted in zip(native[3:], expected):
        assert row['id'] == wanted['id'] and row['actual_stdout'] == wanted['native_stdout']
        line = int(row['actual_stdout'].split('H:', 1)[1].split(':', 1)[0])
        assert line == wanted['notice_line']
        peer_records.append(dict(id=row['id'], source=row['command'][-1],
            source_sha256=row['source_sha256'], cwd=str(ROOT), process=row,
            stdout=row['actual_stdout'], stderr=row['actual_stderr'], observed_line=line, passed=True))
    peer_native.write_text(json.dumps(dict(mode='native-only', passed=True,
        inputs_stable=report['inputs_stable'], head_stable=report['head_stable'],
        runtime=report['runtime'], profile=report['profile'],
        derived_from=str(source_path), records=peer_records), indent=2) + '\n')
    subprocess.run([sys.executable, str(author_state), '--native-report', str(author_native),
        '--output', str(directory / 'author-state')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(peer_state), '--native-report', str(peer_native),
        '--output', str(directory / 'peer-state')], cwd=ROOT, check=True)
    reports = [report] + [json.loads((directory / part / 'report.json').read_bytes())
        for part in ('author-state', 'peer-state')]
    inputs = {}
    for current in reports:
        assert current['passed'] and current['inputs_stable'] and current['head_stable']
        assert current['revision'] == report['revision']
        shared = report['inputs'].keys() & current['inputs'].keys()
        assert shared and all(report['inputs'][path] == current['inputs'][path] for path in shared)
        for path, digest in current['inputs'].items():
            assert path not in inputs or inputs[path] == digest
            inputs[path] = digest
    assert before == fingerprints()
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
