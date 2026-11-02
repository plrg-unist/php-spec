#!/usr/bin/env python3
"""Native-first materialized collection with a rebuffered Closure capture leaf."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_rebuffered_leaf_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_rebuffered_leaf_status.php'
family.CASES = {'rebuffered-leaf-captured-direct-caller': SOURCE.read_bytes(),
                'native-rebuffer-status': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'rebuffered-leaf-captured-direct-caller': 240}
EXPECTED_SHA256 = 'f1c0af0c8bb2cb9d235b32bb4b071a7ce1b9bd129a23c78f12c1d66834e3ed65'
assert hashlib.sha256(family.CASES['rebuffered-leaf-captured-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = 'cba8e0e546db583e99a411eb9daa4b8d33983e7f599761041932bb58a32f1465'
assert hashlib.sha256(family.CASES['native-rebuffer-status']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
