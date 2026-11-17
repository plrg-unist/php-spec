#!/usr/bin/env python3
"""Null-left NaN coalesce instanceof originals retain native observations once."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_sources as runner
import string_offset_request_base_runtime_null_left_nan_coalesce_instanceof_special_concat_leading_key_cases as cases

source_recorded = runner.recorded


def recorded(command, stem, cap):
    if command[0] == str(runner.ROOT / 'bin/php-semantics'):
        command, cap = [*command[:-1], '240'], 270
    return source_recorded(command, stem, cap)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    runner.cases = cases
    runner.recorded = recorded
    passed = runner.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'][str(own.relative_to(runner.ROOT))] = before
    for row in report['rows']:
        source = Path(row['native']['argv'][-1])
        row['native_stdout'] = str(source.with_name('native.stdout'))
        row['native_stderr'] = str(source.with_name('native.stderr'))
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
