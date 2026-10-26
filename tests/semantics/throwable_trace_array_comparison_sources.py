#!/usr/bin/env python3
"""Native-first source checks for finite DIRECT array-valued builtin Throwable traces."""
from pathlib import Path

import global_constant_sources as family
from throwable_trace_array_comparison_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'object-control': ('Throwable property comparison', b'B|'),
    'reference-control': ('Throwable property comparison', b'B|'),
    'cycle-control': ('Throwable property comparison', b'B|'),
}
family.BASELINE = ('Throwable property comparison', b'B|')
family.MODEL_TIMEOUTS = {name: 90 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_trace_array_comparison_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_trace_array_comparison_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
