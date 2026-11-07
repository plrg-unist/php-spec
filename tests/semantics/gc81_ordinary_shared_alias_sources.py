#!/usr/bin/env python3
"""Shared scalar aliases through COW and real last table/CELL disposal."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc81_ordinary_shared_alias.php'
family.CASES = {'ordinary-shared-alias-copy-and-retirement': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'ordinary-shared-alias-copy-and-retirement': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
