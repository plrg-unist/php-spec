#!/usr/bin/env python3
"""No-rebuild array projections of ordinary hook-bearing objects."""
from pathlib import Path

import global_constant_sources as family
from hook_array_projection_review_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {name: 90 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/hook_array_projection_review_cases.py':
            family.sha(family.ROOT / 'tests/semantics/hook_array_projection_review_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
