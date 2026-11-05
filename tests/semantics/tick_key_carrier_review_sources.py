#!/usr/bin/env python3
"""Independent numeric and equal-byte string-carrier key consumers."""
from pathlib import Path

import tick_key_carrier_review_cases as cases
import tick_coalesce_reader_sources as sources


if __name__ == '__main__':
    previous = sources.ticks.fingerprint
    sources.ticks.fingerprint = lambda: {
        **previous(), 'tests/semantics/tick_key_carrier_review_cases.py': sources.ticks.sha(Path(cases.__file__))}
    sources.main(cases.CASES, Path(__file__))
