#!/usr/bin/env python3
"""Native-first inactive weak observer chains, singleton aliases and dead targets."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
PATH = ROOT / 'tests/semantics/gc_inactive_weak_chain_source.php'
SOURCE = PATH.read_bytes()
assert hashlib.sha256(SOURCE).hexdigest() == 'e495ecee1c97d80089eedb1aa95041cf5aa2a2348298309d68271e0a243e6231'
family.CASES = {'observer-chain': SOURCE}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'observer-chain': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [PATH, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
