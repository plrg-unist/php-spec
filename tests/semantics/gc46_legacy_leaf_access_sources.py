#!/usr/bin/env python3
"""Restore the exact M141 separate-leaf original for the access partition fix."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc46_legacy_leaf_access.php'
family.CASES = {'m141-separate-leaf-entry-access': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'m141-separate-leaf-entry-access': 120}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
