#!/usr/bin/env python3
"""Checked quiet NaN-child arithmetic CONCAT sources with native original paths."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_warnings as runner
import string_offset_request_base_nan_child_arithmetic_special_concat_leading_key_cases as cases

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    output = args.output
    if output is None:
        output = Path(tempfile.mkdtemp(prefix='nan-child-arithmetic-special-concat-key-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(output)]
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    runner.cases = cases
    passed = runner.main(model_timeout=90)
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'][str(Path(__file__).resolve().relative_to(runner.ROOT))] = own_hash
    for row in report['rows']:
        source = Path(row['native']['argv'][-1])
        row['native_stdout'] = str(source.with_name('native.stdout'))
        row['native_stderr'] = str(source.with_name('native.stderr'))
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
