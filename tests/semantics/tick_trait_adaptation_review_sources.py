#!/usr/bin/env python3
"""Compare alias-method Tick trace identity, callback abort and retry."""
from pathlib import Path

import tick_trait_adaptation_review_cases as sources
import tick_trait_adaptation_sources as base


previous = base.ticks.fingerprint
base.ticks.fingerprint = lambda: {**previous(), **{
    str(path.relative_to(base.ticks.ROOT)): base.ticks.sha(path)
    for path in [Path(sources.__file__), Path(__file__)]}}


if __name__ == '__main__':
    base.main(sources.CASES, Path(__file__))
