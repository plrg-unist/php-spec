#!/usr/bin/env python3
"""A fetched property array and its COW copy own real Child edges after Key death."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc54_property_array_cow_hold.php'
family.CASES = {'property-array-fetched-cow-key-death': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'property-array-fetched-cow-key-death': 300}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
