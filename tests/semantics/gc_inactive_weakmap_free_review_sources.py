#!/usr/bin/env python3
"""All WeakMap keys unregister before an owning value releases another key."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
PATH = ROOT / 'tests/semantics/gc_inactive_weakmap_unregister_source.php'
SOURCE = PATH.read_bytes()
assert hashlib.sha256(SOURCE).hexdigest() == 'e5cd2d3ef0cd2d73ac1d4a2b4ad65e5573f69f35a60dd2cffc8b2ddf3960c6e3'
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
