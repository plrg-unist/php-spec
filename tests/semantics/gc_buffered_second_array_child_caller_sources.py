#!/usr/bin/env python3
"""Native-first captured array with both childless object entries buffered."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_buffered_second_array_child_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_buffered_second_array_child_status.php'
family.CASES = {'buffered-second-array-child-direct-caller': SOURCE.read_bytes(),
                'native-buffered-second-array-child-status': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'buffered-second-array-child-direct-caller': 240}
EXPECTED_SHA256 = 'e42f4cc6b81317f7a70e94260581b63cb8e4a02b337e6990ef1a79e2196f3037'
assert hashlib.sha256(family.CASES['buffered-second-array-child-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = '1657e96b4d2cd9bbbac7c11acaec3d2295ea3929fb8da43231a830e474c20110'
assert hashlib.sha256(family.CASES['native-buffered-second-array-child-status']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
