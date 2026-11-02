#!/usr/bin/env python3
"""Native-first buffered captured array with two childless object entries."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_two_array_children_caller_source.php'
STATUS = ROOT / 'tests/semantics/gc_two_array_children_status.php'
family.CASES = {'two-array-children-direct-caller': SOURCE.read_bytes(),
                'native-two-array-children-status': STATUS.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'two-array-children-direct-caller': 240}
EXPECTED_SHA256 = 'ad044f87720e870741b30e4944e14336716e10ba8875f74b5b7db095cfb233bd'
assert hashlib.sha256(family.CASES['two-array-children-direct-caller']).hexdigest() == EXPECTED_SHA256
STATUS_SHA256 = '324a92c5ff6415ebaa921c11b78ab6a307903a7803a559b1b6bb718be17652ee'
assert hashlib.sha256(family.CASES['native-two-array-children-status']).hexdigest() == STATUS_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, STATUS, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
