#!/usr/bin/env python3
"""Native-first forward checked-left removal during a missing-right Warning."""
from pathlib import Path

import global_constant_sources as family
from undefined_scalar_compare_checked_unset_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'checked-equal-array-boundary': ('scalar comparison warning changed left operand', b'B|H|'),
    'checked-greater-checked-right-boundary': ('scalar comparison warning changed right operand', b'B|H|'),
}
family.BASELINE = ('scalar comparison warning changed left operand', b'H:1:1:10:1;')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_scalar_compare_checked_unset_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_scalar_compare_checked_unset_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
