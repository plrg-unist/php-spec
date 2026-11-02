#!/usr/bin/env python3
"""Compare crossed Generator ownership sources with pinned PHP."""
import json
from pathlib import Path
import sys

import config_generator_bounded_ownership_cases as cases
import incdec_warnings as runner


if __name__ == '__main__':
    if '--output' not in sys.argv:
        raise SystemExit('the ownership matrix requires --output')
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    before = {name: path.read_bytes() for name, path in cases.SOURCE_FILES.items()}
    runner.cases = cases
    passed = runner.main(model_timeout=240)
    report_path = output / 'report.json'
    report = json.loads(report_path.read_text())
    for row in report['rows']:
        name = row['id']
        row['manual_expected_match'] = (
            (output / name / 'native.stdout').read_bytes() == cases.EXPECTED[name]
            and (output / name / 'native.stderr').read_bytes() == b''
        )
        row['passed'] = row['passed'] and row['manual_expected_match']
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert before == {name: path.read_bytes() for name, path in cases.SOURCE_FILES.items()}
    raise SystemExit(0 if passed and all(row['passed'] for row in report['rows']) else 1)
