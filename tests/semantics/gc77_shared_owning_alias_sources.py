#!/usr/bin/env python3
"""Shared owning ALIA COW with an immediate payload destructor."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc77_shared_owning_alias.php'
family.CASES = {'shared-owning-alias-write-through': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-owning-alias-write-through': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
