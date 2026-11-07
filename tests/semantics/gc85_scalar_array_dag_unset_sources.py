#!/usr/bin/env python3
"""Shallow COW deletion preserves a repeated scalar-only array DAG."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc85_scalar_array_dag_unset.php'
family.CASES = {'repeated-depth-two-scalar-array-delete': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'repeated-depth-two-scalar-array-delete': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
