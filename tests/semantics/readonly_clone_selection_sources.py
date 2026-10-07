#!/usr/bin/env python3
"""Exact clone-maker selection, lifetime and manual-call originals."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

import readonly_clone_sources as callbacks

ROOT = Path(__file__).resolve().parents[2]
TABLE = Path(__file__).with_name('readonly_clone_selection_cases.json')
ROWS = json.loads(TABLE.read_text())['cases']


def snapshot(freeze_path):
    result = callbacks.snapshot(freeze_path)
    for path in (TABLE, Path(__file__).resolve()):
        result['watched'][str(path.relative_to(ROOT))] = {
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'mode': oct(path.stat().st_mode & 0o7777)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    names = args.select.split(',') if args.select else [r['id'] for r in ROWS]
    assert names and len(names) == len(set(names))
    assert all(name in {r['id'] for r in ROWS} for name in names)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='readonly-clone-selection-', dir=ROOT/'.tools')).resolve()
    report = {'passed': False, 'before': before, 'profile': callbacks.cross.invoke.types.PROFILE,
              'selected': names, 'jobs': 1, 'records': []}
    print(out, flush=True)
    try:
        for name in names:
            row = next(r for r in ROWS if r['id'] == name)
            directory = out/name; directory.mkdir()
            path = directory/'source.php'; path.write_bytes(row['source'].encode())
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['source_sha256']
            record = {'case': name, 'source_sha256': row['source_sha256'], 'completed': False}
            report['records'].append(record)
            record['outcome'] = callbacks.source(row, directory, path)
            record['completed'] = True
            print(name, record['outcome']['status'], flush=True)
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = snapshot(args.freeze)
        report['passed'] = report['passed'] and before == report['after']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
