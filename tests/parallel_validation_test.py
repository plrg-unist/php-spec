#!/usr/bin/env python3
"""Reject incomplete shard evidence and compare real sequential/parallel results."""
import base64
import collections
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from parallel_validate import ROOT, aggregate


def synthetic(directory, mutation=None):
    rows = [{'id': f'case/{i}', 'ini': {'short_open_tag': str(i % 2)},
             'status': 'parser_rejection' if i % 3 == 0 else 'pass', '_ordinal': i}
            for i in range(8)]
    summaries = [{'shard': {'index': i, 'count': 4}, 'eligible_count': 8,
                  'stable_implementation': True, 'implementation': {'sha256': 'a' * 64}}
                 for i in range(4)]
    shards = [rows[i::4] for i in range(4)]
    for summary, records in zip(summaries, shards):
        summary.update(tested=len(records), counts=dict(collections.Counter(x['status'] for x in records)))
    if mutation:
        mutation(shards, summaries)
    paths = [directory / f'{i}.jsonl' for i in range(4)]
    for path, records, summary in zip(paths, shards, summaries):
        path.write_text(''.join(json.dumps(row) + '\n' for row in records))
        path.with_suffix('.summary.json').write_text(json.dumps(summary))
    return paths


def replace(mapping, **values):
    mapping.update(values)


def run(command, log, accepted=True):
    with log.open('w') as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
    if (result.returncode == 0) != accepted:
        raise AssertionError(log.read_text())


def comparable_rows(path):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for row in rows:
        lint = row.get('lint', {})
        if 'diagnostic_b64' in lint:
            diagnostic = base64.b64decode(lint['diagnostic_b64'])
            # Only the independently allocated lint fixture pathname varies.
            # Preserve the original reports and every other diagnostic byte.
            pattern = re.escape(str(Path(tempfile.gettempdir())).encode()) + rb'/tmp[a-z0-9_]{8}\.php'
            paths = set(re.findall(pattern, diagnostic))
            assert len(paths) <= 1, 'Unexpected multiple temporary diagnostic paths'
            if paths:
                diagnostic = diagnostic.replace(paths.pop(), b'<lint-fixture>')
            lint['diagnostic_b64'] = base64.b64encode(diagnostic).decode()
    return rows


def main():
    with tempfile.TemporaryDirectory(prefix='php-spec-shards-') as temporary:
        directory = Path(temporary)
        output = directory / 'merged.jsonl'
        summary = aggregate(synthetic(directory), output)
        assert summary['tested'] == 8 and summary['counts'] == {'parser_rejection': 3, 'pass': 5}
        changes = [
            lambda rows, summaries: rows[0].pop(),
            lambda rows, summaries: rows[0].append(copy.deepcopy(rows[0][0])),
            lambda rows, summaries: replace(rows[1][0], _ordinal=0),
            lambda rows, summaries: replace(rows[1][0], id=rows[0][0]['id'], ini=rows[0][0]['ini']),
            lambda rows, summaries: replace(summaries[0], eligible_count=9),
            lambda rows, summaries: replace(summaries[1], stable_implementation=False),
            lambda rows, summaries: replace(summaries[1], implementation={'sha256': 'b' * 64}),
            lambda rows, summaries: replace(summaries[1], tested=7),
            lambda rows, summaries: replace(summaries[1], counts={'pass': 8}),
            lambda rows, summaries: replace(summaries[1], shard={'index': 0, 'count': 4}),
        ]
        for change in changes:
            try:
                aggregate(synthetic(directory, change), output)
            except ValueError:
                pass
            else:
                raise AssertionError('Malformed shard evidence was accepted')
        # Two bounded real groups cover accepted profiles and parser rejections.
        for group in ['encoding-', 'negative-']:
            sequential, parallel = directory / f'{group}sequential.jsonl', directory / f'{group}parallel.jsonl'
            arguments = ['--match', group, '--limit', '4', '--lint-all']
            run([sys.executable, str(ROOT / 'tests/validate.py'), *arguments, '--output', str(sequential)], directory / 'sequential.log')
            run([sys.executable, str(ROOT / 'tests/parallel_validate.py'), *arguments, '--output', str(parallel)], directory / 'parallel.log')
            assert comparable_rows(sequential) == comparable_rows(parallel), f'Ordered observations differ for {group}'
            a, b = (json.loads(path.with_suffix('.summary.json').read_text()) for path in [sequential, parallel])
            assert all(a[key] == b[key] for key in a), f'Summary differs for {group}'
        failed = directory / 'failed.jsonl'
        base = [sys.executable, str(ROOT / 'tests/parallel_validate.py'), '--output', str(failed)]
        for args in [['--unknown-validation-option'], ['--generated', '--limit', '8', '--timeout', '0.001']]:
            failed.with_suffix('.summary.json').write_text('{"stable_implementation":true}')
            run(base + args, directory / 'failed.log', accepted=False)
            assert not failed.with_suffix('.summary.json').exists(), 'Stale success survived child failure/timeout'
    print('Parallel validation: ordered profile/rejection parity, ten malformed shard cases, child failure and timeout passed')


if __name__ == '__main__':
    main()
