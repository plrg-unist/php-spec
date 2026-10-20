#!/usr/bin/env python3
"""Native-first forward scalar comparison second-Warning continuations."""
from pathlib import Path

import global_constant_sources as family
from undefined_scalar_compare_second_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'second-forward-removed-left-boundary': ('scalar comparison warning changed left operand', b'B|H|'),
}
family.BASELINE = ('scalar comparison warning changed right operand', b'H:1:1::10;')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_scalar_compare_second_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_scalar_compare_second_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
