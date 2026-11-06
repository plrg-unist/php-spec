#!/usr/bin/env python3
"""Existing retained-array item-reference acquisition, write and hidden Child."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc72_item_reference_cow.php'
family.CASES = {'retained-array-item-reference': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'retained-array-item-reference': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
