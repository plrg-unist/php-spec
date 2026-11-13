#!/usr/bin/env python3
"""Actual release-constant occurrences preserve fold and fallback distinctions."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_compiler as runner
import startup_version_constants_cases as cases


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    runner.cases, runner.VALUES = cases, cases.VALUES
    passed = runner.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'][str(own.relative_to(runner.ROOT))] = before
    report['constants'] = list(cases.VALUES)
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
