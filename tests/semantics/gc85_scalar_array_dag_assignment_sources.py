#!/usr/bin/env python3
"""A shallow scalar-array COW separates header and selected-item decrements."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc85_scalar_array_dag_assignment.php'
family.CASES = {'scalar-array-dag-assignment': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'scalar-array-dag-assignment': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
