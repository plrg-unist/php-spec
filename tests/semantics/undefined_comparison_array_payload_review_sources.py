#!/usr/bin/env python3
"""Independent reference-cell child arrays against frozen missing NULL."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_array_payload_review_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'P;')
family.MODEL_TIMEOUTS = {name: 60 for name in CASES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_array_payload_review_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_array_payload_review_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
