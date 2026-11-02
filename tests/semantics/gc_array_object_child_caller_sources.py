#!/usr/bin/env python3
"""Native-first collection with one object child in a captured runtime array."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_array_object_child_caller_source.php'
family.CASES = {'array-object-child-captured-direct-caller': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'array-object-child-captured-direct-caller': 240}
EXPECTED_SHA256 = '7ab4e4aa25d90bf3dc38659f39b06a45e5c990bb12f2f0abf118987f641e4357'
assert hashlib.sha256(family.CASES['array-object-child-captured-direct-caller']).hexdigest() == EXPECTED_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
