#!/usr/bin/env python3
"""Compare actual eval/import Tick dispatch and pending-body abort."""
from pathlib import Path

import tick_import_review_cases as sources
import tick_import_sources as base


previous = base.ticks.fingerprint
base.ticks.fingerprint = lambda: {**previous(), **{
    str(path.relative_to(base.ticks.ROOT)): base.ticks.sha(path)
    for path in [Path(sources.__file__), Path(__file__)]}}


if __name__ == '__main__':
    base.main(sources.CASES, Path(__file__))
