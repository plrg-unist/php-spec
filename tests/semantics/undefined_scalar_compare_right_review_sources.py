#!/usr/bin/env python3
"""Independent current-left direct-CV equality and less-than comparisons."""
from pathlib import Path

import global_constant_sources as family
from undefined_scalar_compare_right_review_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'peer-left-unset-has-no-second-native-warning':
        ('scalar comparison warning changed left operand', b'H:1:1:10;'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_scalar_compare_right_review_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_scalar_compare_right_review_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
