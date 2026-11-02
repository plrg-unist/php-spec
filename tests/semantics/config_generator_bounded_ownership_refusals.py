#!/usr/bin/env python3
"""Keep effectful conversion and retained factory Generator outside the admitted rule."""
import json
from pathlib import Path
import sys

import incdec_warnings as runner

HERE = Path(__file__).resolve().parent
SOURCE_FILES = {
    'config-generator-bounded-stringable-refusal': HERE / 'config_generator_bounded_stringable_refusal.php',
    'config-generator-bounded-retained-refusal': HERE / 'config_generator_bounded_retained_refusal.php',
}
CASES = {name: path.read_bytes() for name, path in SOURCE_FILES.items()}
BOUNDARIES = {name: 'CONFIG Generator unpack send outside scalar/key domain' for name in CASES}
EXPECTED_NATIVE = {
    'config-generator-bounded-stringable-refusal': b'B;P;Y0;Y1;T;STR;R:14:6;',
    'config-generator-bounded-retained-refusal': b'B;P;Y0;Y1;T;E:1:6;A:8;L:1;U:1;',
}


if __name__ == '__main__':
    if '--output' not in sys.argv:
        raise SystemExit('the refusal check requires --output')
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    before = {name: path.read_bytes() for name, path in SOURCE_FILES.items()}
    runner.cases = sys.modules[__name__]
    passed = runner.main(model_timeout=240)
    report_path = output / 'report.json'
    report = json.loads(report_path.read_text())
    for row in report['rows']:
        name = row['id']
        row['manual_native_match'] = (
            (output / name / 'native.stdout').read_bytes() == EXPECTED_NATIVE[name]
            and (output / name / 'native.stderr').read_bytes() == b''
        )
        row['passed'] = row['passed'] and row['manual_native_match'] and row['agreement_credit'] == 0
    report['scope'] = 'explicit unsupported exclusions; zero source agreement credit'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert before == {name: path.read_bytes() for name, path in SOURCE_FILES.items()}
    raise SystemExit(0 if passed and all(row['passed'] for row in report['rows']) else 1)
