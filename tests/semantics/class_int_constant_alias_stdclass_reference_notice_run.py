#!/usr/bin/env python3
"""Run integer-constant Notice originals and state checks using fresh local facts."""
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


def peer_native_report(report_path, directory, peer_case):
    report = json.loads(report_path.read_bytes())
    assert report['passed'] and report['inputs_stable'] and report['head_stable']
    assert report['normal_agreements'] == 2
    record, = [row for row in report['records'] if row['id'] == peer_case]
    native = record['native']
    original = Path(native['command'][-1])
    assert record['passed'] and native['exit'] == 0 and not native['timeout']
    assert not native['group_after'] and 'reused_from' not in native
    runtime = report['runtime']['binary_sha256']
    peer = directory / 'peer-native.json'
    peer.write_text(json.dumps(dict(native, id=record['id'],
        source_sha256=record['source_sha256'], profile=report['profile'],
        runtime_sha256=runtime, runtime_sha256_after=runtime,
        mode='native-only', passed=True, derived_from=str(report_path),
        stdout=original.with_name('native.stdout').read_text(),
        stderr=original.with_name('native.stderr').read_text()), indent=2) + '\n')
    return peer


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    tests = ROOT / 'tests/semantics'
    author_cases = tests / 'static_class_int_constant_alias_stdclass_reference_notice_cases.json'
    peer_cases = tests / 'class_int_constant_alias_stdclass_reference_notice_review_cases.json'
    watched = [Path(__file__), author_cases, peer_cases, tests / 'error_handler_run.py']
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = fingerprints()
    directory = Path(tempfile.mkdtemp(prefix='class-int-constant-reference-run-', dir=ROOT / '.tools'))
    print(directory, flush=True)
    cases = json.loads(author_cases.read_bytes()) + json.loads(peer_cases.read_bytes())
    assert len(cases) == len({row['id'] for row in cases}) == 2
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
    peer = peer_native_report(report_path, directory, cases[-1]['id'])
    for part in ('checkpoint', 'post'):
        subprocess.run([sys.executable, str(tests / 'class_int_constant_alias_stdclass_reference_notice_review_state.py'),
            '--native-provenance', str(peer), '--part', part,
            '--output', str(directory / ('peer-' + part))], cwd=ROOT, check=True)
    checkpoint = json.loads((directory / 'peer-checkpoint/report.json').read_bytes())
    controls = json.loads((directory / 'peer-post/report.json').read_bytes())
    assert checkpoint['revision'] == controls['revision']
    assert checkpoint['source_sha256'] == controls['source_sha256'] and checkpoint['inputs'] == controls['inputs']
    assert before == fingerprints()
    return True


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
