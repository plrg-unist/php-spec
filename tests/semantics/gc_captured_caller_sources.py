#!/usr/bin/env python3
"""Native-first materialized collection from a scalar-capturing Closure."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_captured_caller_source.php'
family.CASES = {'scalar-captured-direct-caller': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'scalar-captured-direct-caller': 240}
EXPECTED_SHA256 = 'f5a41c300a730e060f4b7e8bbdc6b0d7ad65a3eb855da19007e357051c202a90'
assert hashlib.sha256(family.CASES['scalar-captured-direct-caller']).hexdigest() == EXPECTED_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
