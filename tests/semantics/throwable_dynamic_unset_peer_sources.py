#!/usr/bin/env python3
"""Differential source checks for independent dynamic-deletion cases."""
from pathlib import Path

import global_constant_sources as family
from throwable_dynamic_unset_order_cases import CASES as ORDER_CASES
from throwable_dynamic_unset_peer_cases import CASES as PEER_CASES

family.CASES = dict(PEER_CASES, **ORDER_CASES)
family.UNSUPPORTED = {}
family.BASELINE = ('Throwable property comparison', b'B|')
family.MODEL_TIMEOUTS = {name: 480 for name in family.CASES}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_dynamic_unset_peer_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_dynamic_unset_peer_cases.py'),
        'tests/semantics/throwable_dynamic_unset_order_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_dynamic_unset_order_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
