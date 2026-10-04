#!/usr/bin/env python3
"""Supply matching CLI argv facts for the startup-symbol order original.

This source does not read the clock, environment or SERVER. Their explicit test
facts are arbitrary; this is not request-provider or whole-profile agreement.
"""
import argparse
import base64
import json
import tempfile
from pathlib import Path

import shutdown_review as runner


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', type=Path, action='append', default=[])
    args = parser.parse_args()
    row = next(row for row in json.loads(Path(__file__).with_name(
        'destructor_cases.json').read_text()) if row['id'] == 'preexisting-argc-global-order')
    row.pop('expected_unsupported')
    b64 = lambda value: base64.b64encode(value.encode()).decode()
    row['request'] = {'env': [[b64('LC_ALL'), b64('C')], [b64('TZ'), b64('UTC')]],
                      'args': [], 'seconds': '0', 'microseconds': 0,
                      'variables': b64('EGPCS'), 'jit': True}
    row['request_scope'] = __doc__
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', dir=runner.ROOT / '.tools') as catalogue:
        json.dump([row], catalogue)
        catalogue.flush()
        runner.CASES = Path(catalogue.name)
        raise SystemExit(0 if runner.run('', [], '', False, args.native_report) else 1)
