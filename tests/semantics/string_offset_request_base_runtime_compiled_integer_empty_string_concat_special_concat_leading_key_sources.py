#!/usr/bin/env python3
"""Compiled integer CONCAT originals retain native observations once."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_sources as runner
import string_offset_request_base_runtime_compiled_integer_empty_string_concat_special_concat_leading_key_cases as cases


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    runner.cases = cases
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
