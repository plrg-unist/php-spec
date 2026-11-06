#!/usr/bin/env python3
"""A shared nested-array DAG survives fetched/COW copies and weak-Key death."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc55_nested_array_cow_hold.php'
family.CASES = {'nested-array-shared-dag-cow-key-death': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'nested-array-shared-dag-cow-key-death': 360}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
