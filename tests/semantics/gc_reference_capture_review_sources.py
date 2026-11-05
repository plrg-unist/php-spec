#!/usr/bin/env python3
"""Native-first COW through distinct and shared captured reference wrappers."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_reference_capture_cow_source.php'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'fd0da9345b478d0a48e69ef3eecda9325270bc0c9c111f85de7e0916f2c6fbd1'
family.CASES = {'reference-payload-cow': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'reference-payload-cow': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
