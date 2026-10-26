#!/usr/bin/env python3
"""Normal source/native comparisons through materialized backing-hook tables."""
from pathlib import Path

import global_constant_sources as family
from backed_hook_table_comparison_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('materialized-property numeric comparison continuation', b'B|')
family.MODEL_TIMEOUTS = {name: 90 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/backed_hook_table_comparison_cases.py':
            family.sha(family.ROOT / 'tests/semantics/backed_hook_table_comparison_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
