#!/usr/bin/env python3
"""Copied shared-CELL deletion and a later genuine CELL/value release."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc79_shared_alias_unset.php'
family.CASES = {'shared-alias-cow-and-ordinary-deletion': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-alias-cow-and-ordinary-deletion': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
