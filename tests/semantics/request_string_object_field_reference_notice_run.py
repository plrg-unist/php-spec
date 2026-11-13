#!/usr/bin/env python3
"""Run fresh request object-field Notice originals, alias bounds and actual state checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import fiber_static_api_sources as source
from scalar_return_producer_cv_reference_notice_run import native_record, recorded

ROOT = Path(__file__).resolve().parents[2]


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    tests = ROOT / 'tests/semantics'
    author_cases = tests / 'request_string_object_field_reference_notice_cases.json'
    peer_cases = tests / 'request_string_stdclass_fields_reference_notice_review_cases.json'
    author_state = tests / 'request_string_object_field_reference_notice_state.py'
    peer_state = tests / 'request_string_stdclass_fields_reference_notice_review_state.py'
    watched = [Path(__file__), author_cases, peer_cases, author_state, peer_state,
        tests / 'scalar_return_producer_cv_reference_notice_run.py', tests / 'error_handler_run.py']
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = fingerprints()
    directory = Path(tempfile.mkdtemp(prefix='request-string-object-field-reference-run-', dir=ROOT / '.tools'))
    print(directory, flush=True)
    cases = json.loads(author_cases.read_bytes()) + json.loads(peer_cases.read_bytes())
    assert len(cases) == len({row['id'] for row in cases}) == 4
    catalogue = directory / 'cases.json'
    catalogue.write_text(json.dumps(cases, indent=2) + '\n')
    source.CASES, source.IMPLEMENTATION = catalogue, Path(__file__)
    source.PREFIX = str(directory / 'sources-')
    source.MODEL_SECONDS, source.PROCESS_SECONDS = 180, 195
    source.recorded = recorded
    if not source.main():
        return False
    source_path, = directory.glob('sources-*/report.json')
    source_report = json.loads(source_path.read_bytes())
    assert source_report['normal_agreements'] == 3 and len(source_report['records']) == 4
    assert before == fingerprints()
    runtime = source_report['runtime']['binary_sha256']
    native = [native_record(row) for row in source_report['records']]
    author_native = directory / 'author-native.json'
    author_native.write_text(json.dumps(dict(mode='native-first', passed=True,
        inputs_stable=source_report['inputs_stable'], head_stable=source_report['head_stable'],
        runtime_sha256=runtime, profile=source_report['profile'],
        derived_from=str(source_path), records=native[:3]), indent=2) + '\n')
    peer = native[-1]
    peer_native = directory / 'peer-native.json'
    peer_native.write_text(json.dumps(dict(peer, mode='native-only',
        inputs_stable=source_report['inputs_stable'], runtime_sha256=runtime,
        runtime_sha256_after=runtime, profile=source_report['profile'],
        stdout=peer['actual_stdout'], stderr=peer['actual_stderr'],
        derived_from=str(source_path)), indent=2) + '\n')
    subprocess.run([sys.executable, str(author_state), '--native-report', str(author_native),
        '--output', str(directory / 'author-state')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(peer_state), '--native-provenance', str(peer_native),
        '--output', str(directory / 'peer-state')], cwd=ROOT, check=True)
    reports = [source_report] + [json.loads((directory / part / 'report.json').read_bytes())
        for part in ('author-state', 'peer-state')]
    inputs = {}
    for report in reports:
        assert report['passed'] and report['inputs_stable'] and report['head_stable']
        assert report['revision'] == source_report['revision']
        shared = source_report['inputs'].keys() & report['inputs'].keys()
        assert shared and all(source_report['inputs'][path] == report['inputs'][path] for path in shared)
        for path, digest in report['inputs'].items():
            assert path not in inputs or inputs[path] == digest
            inputs[path] = digest
    assert before == fingerprints()
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
