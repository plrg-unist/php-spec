#!/usr/bin/env python3
"""Pinned native source for reached same-kind severity steps."""
from pathlib import Path

import global_constant_sources as family
from throwable_builtin_same_state_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'state-severity': 120}
base_fingerprint = family.fingerprint


def fingerprint():
    return dict(base_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/throwable_builtin_same_state_cases.py':
            family.sha(family.ROOT / 'tests/semantics/throwable_builtin_same_state_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
