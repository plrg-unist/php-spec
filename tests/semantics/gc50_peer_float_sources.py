#!/usr/bin/env python3
"""Independent NaN replacement and abrupt old Child cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc50_peer_nan_child_throw.php'
family.CASES = {'nan-replacement-child-throw': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'nan-replacement-child-throw': 300}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
