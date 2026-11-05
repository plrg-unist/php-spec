#!/usr/bin/env python3
"""Independent Match tick originals through the shared exact source harness."""
from pathlib import Path

import tick_match_review_cases as cases
import tick_match_sources as sources


if __name__ == '__main__':
    previous = sources.ticks.fingerprint
    sources.ticks.fingerprint = lambda: {
        **previous(), 'tests/semantics/tick_match_review_cases.py': sources.ticks.sha(Path(cases.__file__))}
    sources.main(cases.CASES, Path(__file__))
