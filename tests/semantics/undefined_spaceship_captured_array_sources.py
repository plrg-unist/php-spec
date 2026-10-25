#!/usr/bin/env python3
"""Original captured-array spaceship sources and explicit domain controls."""
from pathlib import Path

import global_constant_sources as family
from undefined_spaceship_captured_array_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_spaceship_captured_array_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_spaceship_captured_array_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
