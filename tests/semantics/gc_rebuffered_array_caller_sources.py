#!/usr/bin/env python3
"""Native-first second-pass collection with a rebuffered array capture."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_rebuffered_array_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_rebuffered_array_status.php'
family.CASES = {'rebuffered-array-captured-direct-caller': SOURCE.read_bytes(),
                'native-rebuffered-array-status': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'rebuffered-array-captured-direct-caller': 240}
EXPECTED_SHA256 = '084190eb271ba06547698b3fd78bd572c7c68697a6b5623f328d01c3aa72893d'
assert hashlib.sha256(family.CASES['rebuffered-array-captured-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = 'be3ad259304f7c98ea8bd46324c55cd93a05d3add7ec95fd8fa56f3424aaffcf'
assert hashlib.sha256(family.CASES['native-rebuffered-array-status']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
