#!/usr/bin/env python3
"""An ordinary real old view owns the zero-excess COW header until retirement."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc80_ordinary_assignment_cow.php'
family.CASES = {'ordinary-direct-assignment-cow-and-last-view-retirement': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'ordinary-direct-assignment-cow-and-last-view-retirement': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
