#!/usr/bin/env python3
"""Borrowed array lookup versus real reference and same-value assignments."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc75_borrowed_array_writeback.php'
family.CASES = {'borrowed-array-lookup-and-real-assignments': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'borrowed-array-lookup-and-real-assignments': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
