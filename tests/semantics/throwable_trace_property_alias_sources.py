#!/usr/bin/env python3
"""Native-first live property references in finite Throwable trace graphs."""
from pathlib import Path

import global_constant_sources as family
from throwable_trace_property_alias_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'different-class-control': ('Throwable property comparison', b'B|'),
    'object-scalar-control': ('Throwable property comparison', b'B|'),
    'cell-cycle-control': ('Throwable property comparison', b'B|'),
}
family.BASELINE = ('Throwable property comparison', b'B|')
family.MODEL_TIMEOUTS = {name: 90 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_trace_property_alias_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_trace_property_alias_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
