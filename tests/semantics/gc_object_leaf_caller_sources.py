#!/usr/bin/env python3
"""Native-first materialized collection from an object-leaf Closure capture."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_object_leaf_caller_source.php'
family.CASES = {'object-leaf-captured-direct-caller': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'object-leaf-captured-direct-caller': 240}
EXPECTED_SHA256 = '4bdc5d67cc1ab5853d9fb7406857338ebe2065ace47b6cd734209e36c8be36dc'
assert hashlib.sha256(family.CASES['object-leaf-captured-direct-caller']).hexdigest() == EXPECTED_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
