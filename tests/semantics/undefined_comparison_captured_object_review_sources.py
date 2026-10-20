#!/usr/bin/env python3
"""Independent captured ordinary-object snapshots and destructor order."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_captured_object_review_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'P;')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_captured_object_review_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_captured_object_review_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
