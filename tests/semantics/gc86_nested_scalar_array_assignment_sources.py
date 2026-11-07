#!/usr/bin/env python3
"""A nested scalar write separates both mutable headers without GC visits."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc86_nested_scalar_array_assignment.php'
family.CASES = {'nested-scalar-array-assignment': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'nested-scalar-array-assignment': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
