#!/usr/bin/env python3
"""Original live ordinary-object comparisons and internal-object boundaries."""
from pathlib import Path

import global_constant_sources as family
from undefined_comparison_live_object_cases import CASES

family.CASES = CASES
family.UNSUPPORTED = {
    'live-object-internal-entry-boundary': ('error-handler ingress requires a producer continuation', b'B|'),
    'live-object-internal-resume-boundary': ('spaceship warning changed opposing scalar', b'B|H|'),
}
family.BASELINE = ('error-handler ingress requires a producer continuation', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__),
        'tests/semantics/undefined_comparison_live_object_cases.py':
            family.sha(family.ROOT / 'tests/semantics/undefined_comparison_live_object_cases.py')})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
