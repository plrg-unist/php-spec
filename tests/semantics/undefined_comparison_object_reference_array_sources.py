#!/usr/bin/env python3
"""Object-reference arrays against frozen missing NULL."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_object_reference_array_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'object-reference-array-internal-alias-entry-boundary': ('error-handler ingress requires a producer continuation', b'B|'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family.MODEL_TIMEOUTS = {
    'object-reference-array-predicates-no-init': 60,
    'object-reference-array-captured-singleton': 60,
    'object-reference-array-captured-greater-throw': 60,
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_object_reference_array_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_object_reference_array_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
