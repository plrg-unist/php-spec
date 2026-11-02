#!/usr/bin/env python3
"""Compare the two-array COW snapshot regression with pinned PHP."""
import json
from pathlib import Path
import sys

import config_generator_two_owning_array_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    if '--output' not in sys.argv:
        raise SystemExit('the array regression requires --output')
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    runner.cases = cases
    passed = runner.main(model_timeout=240)
    report_path = output / 'report.json'
    report = json.loads(report_path.read_text())
    row = report['rows'][0]
    row['manual_expected_match'] = (
        (output / row['id'] / 'native.stdout').read_bytes() == cases.EXPECTED
        and (output / row['id'] / 'native.stderr').read_bytes() == b''
    )
    row['passed'] = row['passed'] and row['manual_expected_match']
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed and row['passed'] else 1)
