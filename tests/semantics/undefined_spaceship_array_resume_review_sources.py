#!/usr/bin/env python3
"""Independent live-array reference, COW, missing-name and throw originals."""
from pathlib import Path

import global_constant_sources as family
from undefined_spaceship_array_resume_review_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {}
family.BASELINE = ('spaceship warning changed opposing scalar', b'H:1:1:18:1;')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_spaceship_array_resume_review_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_spaceship_array_resume_review_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
