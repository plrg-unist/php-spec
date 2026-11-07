#!/usr/bin/env python3
"""Ordinary COW reference acquisition and real last-old-view retirement."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc80_ordinary_reference_cow.php'
family.CASES = {'ordinary-reference-cow-last-old-view': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'ordinary-reference-cow-last-old-view': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
