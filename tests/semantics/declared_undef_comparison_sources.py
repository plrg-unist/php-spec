#!/usr/bin/env python3
"""Normal source/native comparisons through physical declared UNDEF slots."""
from pathlib import Path

import global_constant_sources as family
from declared_undef_comparison_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('retained declared property-table membership mutation', b'B|H:1|')
family.MODEL_TIMEOUTS = {name: 90 for name in CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/declared_undef_comparison_cases.py':
            family.sha(family.ROOT / 'tests/semantics/declared_undef_comparison_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
