#!/usr/bin/env python3
"""Compare handler-created flat arrays through existing Boolean read records."""
from pathlib import Path

import global_constant_sources as family
from undefined_scalar_compare_array_resume_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'boolean-array-initial-array-boundary': ('error-handler ingress requires a producer continuation', b'B|'),
    'boolean-array-nested-array-boundary': ('scalar comparison warning changed left operand', b'B|H|'),
}
family.BASELINE = ('scalar comparison warning changed right operand', b'H:1:1:10:1;')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        'tests/semantics/undefined_scalar_compare_array_resume_cases.py': family.sha(family.ROOT / 'tests/semantics/undefined_scalar_compare_array_resume_cases.py'),
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
