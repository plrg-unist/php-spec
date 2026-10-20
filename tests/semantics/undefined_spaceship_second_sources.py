#!/usr/bin/env python3
"""Native-first second-Warning spaceship missing-CV warnings."""
from pathlib import Path

import global_constant_sources as family
from undefined_spaceship_second_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {'second-spaceship-removed-left-boundary': ('spaceship warning changed opposing scalar', b'B|H|')}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_spaceship_second_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_spaceship_second_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
