#!/usr/bin/env python3
"""Native-first source checks for warmed builtin Throwable traces."""
from pathlib import Path

import global_constant_sources as family
from throwable_warm_trace_comparison_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'object-arg-control': ('Throwable property comparison', b'B|'),
    'reference-arg-control': ('Throwable property comparison', b'B|'),
    'cycle-arg-control': ('Throwable property comparison', b'B|'),
}
family.BASELINE = ('Throwable property comparison', b'W|')
family.MODEL_TIMEOUTS = {name: 90 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_warm_trace_comparison_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_warm_trace_comparison_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
