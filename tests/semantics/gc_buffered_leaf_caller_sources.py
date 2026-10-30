#!/usr/bin/env python3
"""Native-first materialized collection from a buffered Closure capture leaf."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_buffered_leaf_caller_source.php'
family.CASES = {'buffered-leaf-captured-direct-caller': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'buffered-leaf-captured-direct-caller': 240}
EXPECTED_SHA256 = 'f99329062884360e729fbe091b54b9a8e9c3c703a717440d2681e57b66f1d608'
assert hashlib.sha256(family.CASES['buffered-leaf-captured-direct-caller']).hexdigest() == EXPECTED_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
