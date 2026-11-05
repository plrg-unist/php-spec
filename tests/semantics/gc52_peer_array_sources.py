#!/usr/bin/env python3
"""Independent array COW and last-owner Child cleanup through a WeakMap."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc52_peer_array_cow_throw.php'
family.CASES = {'direct-array-cow-child-throw': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'direct-array-cow-child-throw': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
