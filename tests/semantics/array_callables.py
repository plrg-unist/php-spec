#!/usr/bin/env python3
"""Original-source array callback selection, admission and capture checks."""
import argparse
import json
from pathlib import Path
import tempfile

import user_string

CATALOGUE = Path(__file__).with_name('array_callables_cases.json')


def run(match):
    rows = [row for row in json.loads(CATALOGUE.read_text()) if match in row['id']]
    assert rows, 'no array callable source selected'
    ordinary = [row for row in rows if row.get('profile') != 'file']
    if ordinary:
        out = Path(tempfile.mkdtemp(prefix='array-callable-selection-', dir=user_string.ROOT / '.tools'))
        selected = out / 'cases.json'
        selected.write_text(json.dumps(ordinary, indent=2) + '\n')
        user_string.CASES = selected
        if not user_string.run(''):
            return False
    files = [row for row in rows if row.get('profile') == 'file']
    if files:
        import include_mutable_execution
        include_mutable_execution.CASES = {row['id']: row['source'].encode() for row in files}
        include_mutable_execution.main()
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match) else 1)
