#!/usr/bin/env python3
"""Run the finite-static-source originals and state cuts using fresh local facts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import error_handler_run as recorder
import fiber_static_api_sources as source

ROOT = Path(__file__).resolve().parents[2]


def recorded(command, directory, stem, environment, cap):
    recorder.ROOT = ROOT
    recorder.ENV = environment
    process = recorder.recorded(list(map(str, command)), directory / stem, cap)
    return dict(process, command=process['argv'])


def native_reports(report_path, directory, peer_case):
    report = json.loads(report_path.read_bytes())
    assert report['passed'] and report['inputs_stable'] and report['head_stable']
    assert report['normal_agreements'] == 3
    rows = []
    for record in report['records']:
        native = record['native']
        original = Path(native['command'][-1])
        assert record['passed'] and native['exit'] == 0 and not native['timeout']
        assert not native['group_after'] and 'reused_from' not in native
        stdout, stderr = original.with_name('native.stdout'), original.with_name('native.stderr')
        rows.append(dict(native, id=record['id'], source_sha256=record['source_sha256'],
            passed=True, stdout=str(stdout), stderr=str(stderr),
            actual_stdout=stdout.read_text(), actual_stderr=stderr.read_text()))
    runtime = report['runtime']['binary_sha256']
    common = dict(profile=report['profile'], runtime_sha256=runtime, passed=True,
        derived_from=str(report_path))
    author = directory / 'native-first.json'
    author.write_text(json.dumps(dict(common, mode='native-first', inputs_stable=True,
        head_stable=True, records=rows), indent=2) + '\n')
    peer_row, = [row for row in rows if row['id'] == peer_case]
    peer = directory / 'peer-native.json'
    peer.write_text(json.dumps(dict(peer_row, **common, mode='native-only',
        runtime_sha256_after=runtime, stdout=peer_row['actual_stdout'],
        stderr=peer_row['actual_stderr']), indent=2) + '\n')
    return author, peer


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    tests = ROOT / 'tests/semantics'
    author_cases = tests / 'multi_static_alias_stdclass_reference_notice_cases.json'
    peer_cases = tests / 'finite_static_alias_stdclass_reference_notice_review_cases.json'
    watched = [Path(__file__), author_cases, peer_cases, tests / 'error_handler_run.py']
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = fingerprints()
    directory = Path(tempfile.mkdtemp(prefix='multi-static-reference-run-', dir=ROOT / '.tools'))
    print(directory, flush=True)
    cases = json.loads(author_cases.read_bytes()) + json.loads(peer_cases.read_bytes())
    assert len(cases) == len({row['id'] for row in cases}) == 3
    catalogue = directory / 'cases.json'
    catalogue.write_text(json.dumps(cases, indent=2) + '\n')
    source.CASES = catalogue
    source.PREFIX = str(directory / 'sources-')
    source.IMPLEMENTATION = Path(__file__)
    source.MODEL_SECONDS, source.PROCESS_SECONDS = 180, 195
    source.recorded = recorded
    if not source.main():
        return False
    assert before == fingerprints()
    report_path, = directory.glob('sources-*/report.json')
    author, peer = native_reports(report_path, directory, cases[-1]['id'])
    subprocess.run([sys.executable, str(tests / 'multi_static_alias_stdclass_reference_notice_state.py'),
        '--native-report', str(author), '--output', str(directory / 'author-state')], cwd=ROOT, check=True)
    for part in ('ownership', 'sources'):
        subprocess.run([sys.executable, str(tests / 'finite_static_alias_stdclass_reference_notice_review_state.py'),
            '--native-provenance', str(peer), '--part', part,
            '--output', str(directory / ('peer-' + part))], cwd=ROOT, check=True)
    assert before == fingerprints()
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
