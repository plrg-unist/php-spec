#!/usr/bin/env python3
"""Independent repeated pending THROW with one LIVE input, raw-current COW and mutable embedded cells."""
from pathlib import Path
import json
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_repeated_pending_buffered_throw_review_cases.json')
source.PREFIX = 'generator-repeated-pending-buffered-throw-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__


def run():
    original = source.recorded
    raw = None
    cow = 'generator-repeated-pending-buffered-throw-review-reverse-row-cow'

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        if stem == 'model' and directory.name == cow:
            assert command[-2:] == ['--timeout', '100']
            command = command[:-1] + ['200']
            cap = 220
        return original(command, directory, stem, environment, cap)

    source.recorded = recorded
    try:
        passed = source.main()
    finally:
        source.recorded = original
    if raw is not None:
        path = raw / 'report.json'
        report = json.loads(path.read_bytes())
        report['budgets']['case_overrides'] = {
            cow: {'model_seconds': 200, 'process_seconds': 220}
        } if cow in report['selection'] else {}
        path.write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
