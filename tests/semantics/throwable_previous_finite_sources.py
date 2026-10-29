#!/usr/bin/env python3
"""Native-first finite canonical Throwable paths without numeric ceilings."""
from pathlib import Path

import global_constant_sources as family
from throwable_previous_finite_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('Throwable property comparison', b'B|')
family.MODEL_TIMEOUTS = {name: 900 for name in CASES}
family.MODEL_TIMEOUTS['deep-base-class-skip'] = 360
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_previous_finite_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_previous_finite_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
