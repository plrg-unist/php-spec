#!/usr/bin/env python3
"""Native-first inherited public images through visited Throwable traces."""
from pathlib import Path

import global_constant_sources as family
from throwable_inheritance_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {name: ('Throwable property comparison', b'B|')
    for name in ('inherited-private-layout-control', 'stdclass-parent-control')}
family.BASELINE = ('Throwable property comparison', b'B|')
family.MODEL_TIMEOUTS = {name: 480 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_inheritance_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_inheritance_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
