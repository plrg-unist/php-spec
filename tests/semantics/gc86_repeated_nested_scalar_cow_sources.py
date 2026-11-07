#!/usr/bin/env python3
"""Two nested separations preserve the old scalar view and real later drops."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc86_repeated_nested_scalar_cow.php'
family.CASES = {'repeated-nested-scalar-write-and-real-drop': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'repeated-nested-scalar-write-and-real-drop': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
