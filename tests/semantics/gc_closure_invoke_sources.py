#!/usr/bin/env python3
"""Native-first materialized collection from explicit Closure::__invoke."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_closure_invoke_source.php'
family.CASES = {'explicit-real-closure-invoke': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'explicit-real-closure-invoke': 240}
EXPECTED_SHA256 = 'e2da1cf5b35cee02722bd512ca005942a0d6991b1fe494c27e7cab2fcb0f9603'
assert hashlib.sha256(family.CASES['explicit-real-closure-invoke']).hexdigest() == EXPECTED_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
