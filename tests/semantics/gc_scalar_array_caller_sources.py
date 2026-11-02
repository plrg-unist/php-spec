#!/usr/bin/env python3
"""Native-first direct Closure with scalar and mutable array captures."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_scalar_array_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_scalar_array_capture_order.php'
family.CASES = {'scalar-array-captured-direct-caller': SOURCE.read_bytes(),
                'native-scalar-array-capture-order': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'scalar-array-captured-direct-caller': 240}
EXPECTED_SHA256 = '02109ae9d222288f941f2750b0400b6be361dd871a631fa93560b552700e621a'
assert hashlib.sha256(family.CASES['scalar-array-captured-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = 'f5d7317ea1f0aff24acf61445b6825cbed718b3688e49c282ee9fb1fd7b52222'
assert hashlib.sha256(family.CASES['native-scalar-array-capture-order']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
