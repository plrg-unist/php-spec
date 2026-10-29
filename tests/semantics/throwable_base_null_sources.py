#!/usr/bin/env python3
"""Native-first base Throwable NULL-previous captured-graph fallback sources."""
from pathlib import Path

import global_constant_sources as family
from throwable_base_null_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {name: ('Throwable property comparison', b'B|')
    for name in ('reached-method-control',)}
family.BASELINE = ('Throwable property comparison', b'C|-1:1|W|1:')
family.MODEL_TIMEOUTS = {name: 240 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_base_null_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_base_null_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
