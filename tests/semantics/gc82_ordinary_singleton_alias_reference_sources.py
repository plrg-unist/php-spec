#!/usr/bin/env python3
"""A singleton scalar wrapper unwraps before a fresh COW item reference."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc82_ordinary_singleton_alias_reference.php'
family.CASES = {'ordinary-singleton-alias-reference-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'ordinary-singleton-alias-reference-cow': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
