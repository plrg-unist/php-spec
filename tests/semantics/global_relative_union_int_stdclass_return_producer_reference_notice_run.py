#!/usr/bin/env python3
"""Run empty-namespace ordered relative class/int RETURN declarations, combined FORMAL aliases and the unchanged array-return control."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import fiber_static_api_sources as source
import global_relative_union_int_stdclass_return_producer_reference_notice_state as author
import relative_union_int_stdclass_return_producer_reference_notice_review_state as peer
from scalar_return_producer_cv_reference_notice_run import native_record, recorded

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', type=Path, action='append', default=[])
    args = parser.parse_args()
    tests = ROOT / 'tests/semantics'
    watched = [Path(__file__), author.CATALOGUE, peer.CATALOGUE]
    watched += sorted({Path(module.__file__).absolute() for module in sys.modules.values()
        if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == tests})
    watched += [tests / name for name in (
        'global_relative_union_int_stdclass_return_producer_reference_notice_sources.py',
        'relative_union_int_stdclass_return_producer_reference_notice_review_sources.py', 'profile.json')]
    watched += [ROOT / name for name in ('tests/validate.py', 'tests/corpus.py',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    native_previous = {}
    for path in args.native_report:
        path = path.resolve()
        native = json.loads(path.read_bytes())
        assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
        watched.append(path)
        for row in native['records']:
            assert row['id'] not in native_previous
            native_previous[row['id']] = row
            watched += [Path(row['command'][-1]), Path(row['stdout']), Path(row['stderr'])]
    fingerprints = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = fingerprints()
    directory = Path(tempfile.mkdtemp(prefix='global-relative-union-int-stdclass-return-producer-reference-run-', dir=ROOT / '.tools'))
    print(directory, flush=True)
    cases = json.loads(author.CATALOGUE.read_bytes()) + json.loads(peer.CATALOGUE.read_bytes())
    assert len(cases) == len({row['id'] for row in cases}) == 4
    assert sum(row['new_support_credit'] for row in cases) == 3
    if args.native_report:
        assert set(native_previous) == {row['id'] for row in cases}
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
    assert source_report['normal_agreements'] == len(source_report['records']) == 4
    assert before == fingerprints()
    native = [native_previous[row['id']] if args.native_report else native_record(row)
        for row in source_report['records']]
    reports = [source_report]
    for role, records, module in (('author', native[:2], author), ('peer', native[2:], peer)):
        native_path = directory / (role + '-native.json')
        native_path.write_text(json.dumps(dict(mode='native-first', passed=True,
            inputs_stable=source_report['inputs_stable'], head_stable=source_report['head_stable'],
            runtime_sha256=source_report['runtime']['binary_sha256'], profile=source_report['profile'],
            derived_from=str(source_path), records=records), indent=2) + '\n')
        subprocess.run([sys.executable, '-B', module.__file__, '--native-report', str(native_path),
            '--output', str(directory / (role + '-state'))], cwd=ROOT, check=True)
        reports.append(json.loads((directory / (role + '-state') / 'report.json').read_bytes()))
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
