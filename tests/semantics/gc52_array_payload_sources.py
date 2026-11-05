#!/usr/bin/env python3
"""A real fetched array owner delays weak-Key payload cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc52_fetched_array_key_death.php'
family.CASES = {'fetched-array-held-across-key-death': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'fetched-array-held-across-key-death': 240}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
