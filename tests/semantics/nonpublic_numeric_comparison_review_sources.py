#!/usr/bin/env python3
"""Normal numeric comparison callbacks through non-public materialized slots."""
from pathlib import Path

import global_constant_sources as family
from nonpublic_numeric_comparison_review_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('materialized-property numeric comparison continuation', b'B|')
family.MODEL_TIMEOUTS = {name: 90 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/nonpublic_numeric_comparison_review_cases.py':
            family.sha(family.ROOT / 'tests/semantics/nonpublic_numeric_comparison_review_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
