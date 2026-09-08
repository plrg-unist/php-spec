#!/usr/bin/env python3
"""Run deterministic validation shards and verify a complete ordered merge."""
import argparse
import collections
from contextlib import ExitStack
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from validate import implementation_fingerprint

ROOT = Path(__file__).resolve().parents[1]
FAILURES = {'failure', 'acceptance_mismatch', 'unreviewed_phase_difference',
            'ast_roundtrip_failure', 'fixture_expectation_failure', 'missing_fixture',
            'invalid_container'}


def aggregate(paths, output):
    summaries = [json.loads(path.with_suffix('.summary.json').read_text()) for path in paths]
    count = len(paths)
    if not count:
        raise ValueError('No shards')
    first = summaries[0]
    total = first['eligible_count']
    if not isinstance(total, int) or total < 0:
        raise ValueError('Invalid eligible input count')
    for index, summary in enumerate(summaries):
        if (summary.get('shard') != {'index': index, 'count': count}
                or summary.get('eligible_count') != total
                or summary.get('stable_implementation') is not True
                or summary.get('implementation') != first['implementation']):
            raise ValueError('Shard configuration or implementation fingerprint differs')
    counts, nodes, identities = collections.Counter(), {}, set()
    child_counts = [collections.Counter() for _ in paths]
    with ExitStack() as stack:
        readers = [stack.enter_context(path.open()) for path in paths]
        writer = stack.enter_context(output.open('w'))
        for ordinal in range(total):
            index = ordinal % count
            line = readers[index].readline()
            if not line:
                raise ValueError(f'Missing ordinal {ordinal} from shard {index}')
            row = json.loads(line)
            if row.pop('_ordinal', None) != ordinal:
                raise ValueError(f'Duplicate, missing or misplaced ordinal {ordinal}')
            identity = (row['id'], json.dumps(row.get('ini', {}), sort_keys=True))
            if identity in identities:
                raise ValueError('Duplicate source/profile identity: ' + row['id'])
            identities.add(identity)
            counts[row['status']] += 1
            child_counts[index][row['status']] += 1
            for node in row.get('nodes', []):
                if len(nodes.setdefault(node, [])) < 3:
                    nodes[node].append(row['id'])
            writer.write(json.dumps(row, separators=(',', ':')) + '\n')
        if any(reader.read() for reader in readers):
            raise ValueError('Unexpected trailing shard records')
    for summary, observed in zip(summaries, child_counts):
        if summary['counts'] != dict(observed) or summary['tested'] != sum(observed.values()):
            raise ValueError('Shard summary does not match its records')
    result = {'tested': total, 'counts': dict(counts), 'nodes': nodes,
              'implementation': first['implementation'], 'stable_implementation': True,
              'shards': count, 'eligible_count': total}
    output.with_suffix('.summary.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--timeout', type=float, default=18000, help='Whole-run timeout in seconds')
    parser.add_argument('--output', type=Path, default=ROOT / 'coverage/results-corpus.jsonl')
    args, forwarded = parser.parse_known_args()
    if args.jobs < 1 or args.timeout <= 0 or any(value.startswith('--shard') for value in forwarded):
        parser.error('Positive jobs/timeout required; the launcher owns --shard')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    directory = args.output.with_suffix('.shards')
    directory.mkdir(parents=True, exist_ok=True)
    paths = [directory / f'{index}.jsonl' for index in range(args.jobs)]
    fingerprint = implementation_fingerprint()
    processes, handles = [], []
    deadline = time.monotonic() + args.timeout
    try:
        # Remove old summaries first: a crashed child must not reuse prior success.
        args.output.with_suffix('.summary.json').unlink(missing_ok=True)
        for index, path in enumerate(paths):
            path.unlink(missing_ok=True)
            path.with_suffix('.summary.json').unlink(missing_ok=True)
            log = path.with_suffix('.log').open('w')
            handles.append(log)
            command = [sys.executable, str(ROOT / 'tests/validate.py'), *forwarded,
                       '--shard', f'{index}/{args.jobs}', '--output', str(path)]
            processes.append(subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                               start_new_session=True))
        exits = [process.wait(timeout=max(0.001, deadline - time.monotonic())) for process in processes]
        if any(exits):
            raise RuntimeError(f'Validation shard failed: exits={exits}; logs in {directory}')
        summary = aggregate(paths, args.output)
        if summary['implementation'] != fingerprint or implementation_fingerprint() != fingerprint:
            raise RuntimeError('Implementation changed across the complete parallel run')
        if FAILURES.intersection(key for key, value in summary['counts'].items() if value):
            raise RuntimeError('Merged validation contains unresolved failures')
        print(json.dumps(summary, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        args.output.with_suffix('.summary.json').unlink(missing_ok=True)
        print(f'Parallel validation failed: {error}', file=sys.stderr)
        return 1
    finally:
        for process in processes:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
        for handle in handles:
            handle.close()


if __name__ == '__main__':
    raise SystemExit(main())
