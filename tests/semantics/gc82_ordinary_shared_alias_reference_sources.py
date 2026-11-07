#!/usr/bin/env python3
"""Ordinary shared quiet aliases reuse one CELL after reference-acquisition COW."""
from pathlib import Path
import hashlib
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc82_ordinary_shared_alias_reference.php'
CASE = 'ordinary-shared-alias-reference-copy-and-retirement'
family.CASES = {CASE: SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {CASE: 360}
original_fingerprint = family.fingerprint


def fingerprint():
    result = original_fingerprint()
    for p in (SOURCE, Path(__file__)):
        result[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
