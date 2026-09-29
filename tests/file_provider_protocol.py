#!/usr/bin/env python3
"""The adapter authenticates finite file-resolution facts before resume."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'frontend'))
import wire


def b64(value):
    return base64.b64encode(value).decode()


def call(worker, packet):
    worker.stdin.write(wire.dumps(packet) + '\n')
    worker.stdin.flush()
    line = worker.stdout.readline()
    assert line, worker.stderr.read()
    return wire.loads(line)


def main():
    worker = subprocess.Popen([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True)
    try:
        caller = b64(b'/snapshot/main.php')
        requested = b64(b'parts/one.php')
        row = {'caller': caller, 'requested': requested, 'status': 'opened',
               'resolved': b64(b'/snapshot/parts/one.php'),
               'opened': b64(b'/snapshot/real/one.php'),
               'source': b64(b'<?php return 7;')}
        snapshot = {'version': 1, 'main': caller, 'cwd': b64(b'/snapshot'),
                    'include_path': b64(b'.:'), 'entries': [row]}
        pending = {'id': '0', 'caller': caller, 'requested': requested}
        response = {'id': '0', **row}
        packet = {'op': 'check_file_resolve', 'snapshot': snapshot,
                  'pending': pending, 'response': response}
        checked = call(worker, packet)
        assert checked['ok'] and checked['opened'] == row['opened']
        fallback = copy.deepcopy(packet)
        fallback['snapshot']['entries'][0]['resolved'] = None
        fallback['response']['resolved'] = None
        assert call(worker, fallback)['resolved'] is None

        negatives = []
        for field, changed in (('id', '1'), ('caller', b64(b'/snapshot/other.php')),
                               ('requested', b64(b'parts/two.php')),
                               ('resolved', b64(b'/snapshot/other.php')),
                               ('opened', b64(b'/snapshot/real/other.php')),
                               ('source', b64(b'<?php return 8;'))):
            bad = copy.deepcopy(packet)
            bad['response'][field] = changed
            negatives.append(bad)
        for changed in ('00', '-1'):
            bad = copy.deepcopy(packet)
            bad['pending']['id'] = changed
            negatives.append(bad)
        for changed in (b64(b'/other'), '!!!'):
            bad = copy.deepcopy(packet)
            bad['pending']['requested'] = changed
            negatives.append(bad)
        for change in (
            lambda s: s['entries'].append(copy.deepcopy(row)),
            lambda s: s['entries'].append({**row, 'requested': b64(b'alias.php'),
                                            'source': b64(b'<?php return 9;')}),
            lambda s: s.update(include_path=b64(b'.')),
            lambda s: s.update(cwd=''),
            lambda s: s['entries'][0].update(extra=True),
        ):
            bad = copy.deepcopy(packet)
            change(bad['snapshot'])
            negatives.append(bad)
        for bad in negatives:
            assert call(worker, bad)['ok'] is False
        forged_fallback = copy.deepcopy(fallback)
        forged_fallback['response']['resolved'] = row['resolved']
        assert call(worker, forged_fallback)['ok'] is False
        negatives.append(forged_fallback)

        for status, fields in (
            ('missing', {'stream_error': b64(b'No such file or directory')}),
            ('open_failure', {'resolved': b64(b'/snapshot/parts/one.php'),
                              'stream_error': b64(b'Permission denied')}),
        ):
            branch = copy.deepcopy(packet)
            branch['snapshot']['entries'] = [{'caller': caller, 'requested': requested,
                                             'status': status, **fields}]
            branch['response'] = {'id': '0', **branch['snapshot']['entries'][0]}
            assert call(worker, branch)['ok']
        assert call(worker, packet)['ok']  # A failed probe did not poison the service.
    finally:
        worker.stdin.close()
        assert worker.wait(timeout=5) == 0, worker.stderr.read()
    print(json.dumps({'result': 'pass', 'open': 1, 'failure_facts': 2,
                      'forged_or_ambiguous': len(negatives)}))


if __name__ == '__main__':
    main()
