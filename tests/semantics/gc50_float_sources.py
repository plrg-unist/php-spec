#!/usr/bin/env python3
"""Validated double zvals retain float truth diagnostics and ordinary cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc50_float_matrix.php'
family.CASES = {'float-matrix-copy-quiet-mixed-free': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'float-matrix-copy-quiet-mixed-free': 300}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
