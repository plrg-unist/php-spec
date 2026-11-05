#!/usr/bin/env python3
"""One combined ordinary-reference Closure and A95 Generator identity source."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
PATH = ROOT / 'tests/semantics/gc_reference_capture_a95_source.php'
EXPECTED = '499587f8ba41e815bcb198b975077dba83fe8db9e2ffab40ae715af3c0948636'
assert hashlib.sha256(PATH.read_bytes()).hexdigest() == EXPECTED
family.CASES = {'a95-retired-generator-cell': PATH.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'a95-retired-generator-cell': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [PATH, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
