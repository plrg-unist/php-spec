#!/usr/bin/env python3
"""Native-first scalar spaceship warnings using the ordinary source recorder."""
from pathlib import Path

import global_constant_sources as family
from undefined_spaceship_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        'tests/semantics/undefined_spaceship_cases.py': family.sha(family.ROOT / 'tests/semantics/undefined_spaceship_cases.py'),
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
