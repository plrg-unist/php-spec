#!/usr/bin/env python3
"""Independent coalesce tick sources through the shared exact source harness."""
from pathlib import Path

import tick_coalesce_review_cases as cases
import tick_coalesce_sources as sources


if __name__ == '__main__':
    previous = sources.ticks.fingerprint
    sources.ticks.fingerprint = lambda: {
        **previous(), 'tests/semantics/tick_coalesce_review_cases.py': sources.ticks.sha(Path(cases.__file__))}
    sources.main(cases.CASES, producer=Path(__file__))
