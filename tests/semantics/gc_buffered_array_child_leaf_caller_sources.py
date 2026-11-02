#!/usr/bin/env python3
"""Native-first buffered captured array with a buffered object child."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_buffered_array_child_leaf_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_buffered_array_child_leaf_status.php'
family.CASES = {'buffered-array-child-leaf-direct-caller': SOURCE.read_bytes(),
                'native-buffered-array-child-leaf-status': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'buffered-array-child-leaf-direct-caller': 240}
EXPECTED_SHA256 = '4e5add5e0b2ce06c5bcb30391efe99338fad59f596b3116dff2d7742787e3621'
assert hashlib.sha256(family.CASES['buffered-array-child-leaf-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = '6719a60edb111269d66dfc279ad3de82ed510f912ff562915ee3e7a81c3918e2'
assert hashlib.sha256(family.CASES['native-buffered-array-child-leaf-status']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
