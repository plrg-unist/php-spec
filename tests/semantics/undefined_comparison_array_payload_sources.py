#!/usr/bin/env python3
"""Original flat child-array payloads behind comparison reference entries."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_array_payload_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'array-payload-child-reference-ingress-boundary': ('error-handler ingress requires a producer continuation', b'B|'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family.MODEL_TIMEOUTS = {
    'array-payload-captured-singleton': 60,
    'array-payload-live-replacement': 60,
    'array-payload-empty-child-predicates-no-init': 60,
    'array-payload-captured-greater-throw': 60,
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_array_payload_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_array_payload_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
