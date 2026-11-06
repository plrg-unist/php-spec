#!/usr/bin/env python3
"""Repeated fresh Child throws preserve a finite Previous chain and later read."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc65_finite_previous_later_read.php'
family.CASES = {'finite-previous-later-read': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family.BASELINE = ('further Child throw during WeakMap current-row cleanup',
                   b'S|O|1|B|1|C|1|1|1|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
