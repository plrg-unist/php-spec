#!/usr/bin/env python3
"""Independent reversed both-missing comparisons and warning order."""
from pathlib import Path

import global_constant_sources as family
from undefined_scalar_compare_both_reversed_review_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'peer-both-missing-left-remains-missing':
        ('scalar comparison warning changed left operand', b'H:1::1:8;'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_scalar_compare_both_reversed_review_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_scalar_compare_both_reversed_review_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
