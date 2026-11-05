#!/usr/bin/env python3
"""Occupied WeakMap replacement stays outside first-insertion Value admission."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc37_value_child_occupied_replacement.php'
family.CASES = {'occupied-replacement-unsupported': SOURCE.read_bytes()}
family.UNSUPPORTED = {'occupied-replacement-unsupported':
    ('WeakMap dimension protocol outside first insertion', b'B|')}
family.MODEL_TIMEOUTS = {'occupied-replacement-unsupported': 120}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
