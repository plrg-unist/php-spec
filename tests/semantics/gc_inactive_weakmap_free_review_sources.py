#!/usr/bin/env python3
"""All WeakMap keys unregister before an owning value releases another key."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
PATH = ROOT / 'tests/semantics/gc_inactive_weakmap_unregister_source.php'
SOURCE = PATH.read_bytes()
assert hashlib.sha256(SOURCE).hexdigest() == 'aeb69b390ea47d39f7bd235d4fc3baed5c22ae87c5ed98d69f70731e74251919'
family.CASES = {'unregister-all-before-values': SOURCE}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'unregister-all-before-values': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [PATH, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
