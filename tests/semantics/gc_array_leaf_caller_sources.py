#!/usr/bin/env python3
"""Native-first materialized collection with a mutable array capture leaf."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_array_leaf_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_array_leaf_status.php'
family.CASES = {'array-leaf-captured-direct-caller': SOURCE.read_bytes(),
                'native-array-status': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'array-leaf-captured-direct-caller': 240}
EXPECTED_SHA256 = '201e4a643717193f04bd037fa06696d945c576c194000b0467a3f1176cd4d40b'
assert hashlib.sha256(family.CASES['array-leaf-captured-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = 'edda7c17ffca78b05a1de79685b0862df73b61a4576b651270adcddaeb70e44c'
assert hashlib.sha256(family.CASES['native-array-status']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
