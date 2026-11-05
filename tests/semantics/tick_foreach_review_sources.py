#!/usr/bin/env python3
"""Independent Foreach target originals through the exact source harness."""
from pathlib import Path

import tick_foreach_review_cases as cases
import tick_foreach_sources as sources


if __name__ == '__main__':
    previous = sources.ticks.fingerprint
    sources.ticks.fingerprint = lambda: {
        **previous(), 'tests/semantics/tick_foreach_review_cases.py': sources.ticks.sha(Path(cases.__file__))}
    sources.main(cases.CASES, Path(__file__))
