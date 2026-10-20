#!/usr/bin/env python3
"""Original flat ordinary-object arrays against frozen missing NULL."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_object_array_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'object-array-alias-entry-boundary': ('error-handler ingress requires a producer continuation', b'B|'),
    'object-array-nested-resume-boundary': ('spaceship warning changed opposing scalar', b'B|H|'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family.MODEL_TIMEOUTS = {
    'object-array-predicates-no-init': 60,
    'object-array-captured-greater-throw': 60,
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_object_array_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_object_array_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
