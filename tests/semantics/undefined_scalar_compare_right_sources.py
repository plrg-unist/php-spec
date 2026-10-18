#!/usr/bin/env python3
"""Native-first scalar equality and less-than missing-right warnings."""
from pathlib import Path

import global_constant_sources as family
from undefined_scalar_compare_right_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {'left-array-boundary': ('scalar comparison warning changed left operand', b'B|H|')}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family.MODEL_TIMEOUTS = {'right-scalar-tags-equality': 90}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_scalar_compare_right_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_scalar_compare_right_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
