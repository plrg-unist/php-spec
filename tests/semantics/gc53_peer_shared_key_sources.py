#!/usr/bin/env python3
"""Selective shared-Key Map retirement preserves the other array payload owner."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc53_peer_shared_key_array_throw.php'
family.CASES = {'shared-key-array-map-first-throw': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-key-array-map-first-throw': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
