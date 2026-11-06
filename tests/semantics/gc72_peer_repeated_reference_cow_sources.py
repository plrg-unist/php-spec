#!/usr/bin/env python3
"""Item reference COW wraps only the new table and preserves old Child edges."""
from pathlib import Path

import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc72_peer_repeated_reference_cow.php'
family.CASES = {'repeated-child-item-reference-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'repeated-child-item-reference-cow': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
