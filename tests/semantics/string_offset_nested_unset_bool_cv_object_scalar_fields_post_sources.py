#!/usr/bin/env python3
"""Scalar-field originals; native executes once and exact bytes are reused."""
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_sources as runner
import string_offset_nested_unset_bool_cv_object_scalar_fields_post_cases as cases

RECORDED = runner.recorded


def recorded(argv, prefix, cap):
    if argv[0] == str(runner.ROOT / 'bin/php-semantics'):
        assert argv[-2:] == ['--timeout', '90'] and cap == 120
        argv = [*argv[:-1], '120']
        cap = 150
    return RECORDED(argv, prefix, cap)


if __name__ == '__main__':
    runner.cases = cases
    runner.recorded = recorded
    passed = runner.main()
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['scope'] = ('Fresh scalar-field stdClass Unsupported baseline/source0' if '--baseline' in sys.argv else
                       'Production-SL scalar-field stdClass DIRECT/ALIAS postvalues with saved native observations')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
