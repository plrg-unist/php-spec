#!/usr/bin/env python3
"""Native-first buffered captured array with one ordinary object child."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_rebuffered_array_child_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_rebuffered_array_child_status.php'
family.CASES = {'rebuffered-array-child-captured-direct-caller': SOURCE.read_bytes(),
                'native-rebuffered-array-child-status': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'rebuffered-array-child-captured-direct-caller': 240}
EXPECTED_SHA256 = '02675d819f15576db9ee7ae33448f405ed941bb16cb46b15ee18dccc92019d08'
assert hashlib.sha256(family.CASES['rebuffered-array-child-captured-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = '01683dc6731ee3f936eec765c12636de7cf2f30beb88bea6355b8dd823f92dcc'
assert hashlib.sha256(family.CASES['native-rebuffered-array-child-status']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
