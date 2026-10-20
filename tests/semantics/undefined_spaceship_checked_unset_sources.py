#!/usr/bin/env python3
"""Native-first checked-left removal during a spaceship Warning."""
from pathlib import Path

import global_constant_sources as family
from undefined_spaceship_checked_unset_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('spaceship warning changed opposing scalar', b'H:1:1:10:1;')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_spaceship_checked_unset_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_spaceship_checked_unset_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
