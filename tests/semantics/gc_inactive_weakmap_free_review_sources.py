#!/usr/bin/env python3
"""All WeakMap keys unregister before nested value release and fatal order."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
PATH = ROOT / 'tests/semantics/gc_inactive_weakmap_unregister_source.php'
SOURCE = PATH.read_bytes()
assert hashlib.sha256(SOURCE).hexdigest() == 'aeb69b390ea47d39f7bd235d4fc3baed5c22ae87c5ed98d69f70731e74251919'
ORDER_PATH = ROOT / 'tests/semantics/gc_inactive_weakmap_unregister_order_source.php'
ORDER_SOURCE = ORDER_PATH.read_bytes()
assert hashlib.sha256(ORDER_SOURCE).hexdigest() == '2cfd60df12a1d12f3c1fcbc8e0f6dd2c049560910b60a86740240bce8f40000b'
family.CASES = {'unregister-all-before-values': SOURCE,
                'unregister-before-nested-fatal': ORDER_SOURCE}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
family.MODEL_STATUSES = {'unregister-before-nested-fatal': 'php_error'}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [PATH, ORDER_PATH, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
