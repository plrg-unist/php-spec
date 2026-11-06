#!/usr/bin/env python3
"""Compare inherited method default Closure scope, callback abort and retry."""
from pathlib import Path

import tick_callable_parameter_review_cases as sources
import tick_callable_parameter_sources as base


previous = base.ticks.fingerprint
base.ticks.fingerprint = lambda: {**previous(), **{
    str(path.relative_to(base.ticks.ROOT)): base.ticks.sha(path)
    for path in [Path(sources.__file__), Path(__file__)]}}


if __name__ == '__main__':
    base.main(sources.CASES, {}, Path(__file__))
