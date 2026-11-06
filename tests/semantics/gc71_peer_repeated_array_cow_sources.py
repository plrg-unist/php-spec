#!/usr/bin/env python3
"""A credited original array retains repeated Child edges across visible COW."""
from pathlib import Path

import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc71_peer_repeated_array_cow.php'
family.CASES = {'repeated-child-hidden-array-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'repeated-child-hidden-array-cow': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
