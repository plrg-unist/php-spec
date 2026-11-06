#!/usr/bin/env python3
"""Occupied writes keep the current loop Value while publishing a used result."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc58_current_row_object_replacement.php'
family.CASES = {'current-object-occupied-write-protected-loop-value': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'current-object-occupied-write-protected-loop-value': 360}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
