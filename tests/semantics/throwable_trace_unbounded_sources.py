#!/usr/bin/env python3
"""Native-first finite-heap captured graph comparison beyond depth sixteen."""
from pathlib import Path

import global_constant_sources as family
from throwable_trace_unbounded_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('Throwable property comparison', b'B|')
family.MODEL_TIMEOUTS = {name: 240 for name in CASES}
family.MODEL_TIMEOUTS.update({
    'deep-shared-dag-and-tail-skip': 360,
    'deep-cell-array-retarget': 360})
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_trace_unbounded_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_trace_unbounded_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
