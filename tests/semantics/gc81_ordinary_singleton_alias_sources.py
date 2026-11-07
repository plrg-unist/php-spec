#!/usr/bin/env python3
"""An ordinary singleton scalar wrapper unwraps on COW and retires with the old view."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc81_ordinary_singleton_alias.php'
family.CASES = {'ordinary-singleton-scalar-alias-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'ordinary-singleton-scalar-alias-cow': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
