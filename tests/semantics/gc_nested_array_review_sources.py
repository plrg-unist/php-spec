#!/usr/bin/env python3
"""Native-first independent self-copy snapshot under the rooted GC caller."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_nested_array_self_copy_source.php'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '9a9bc26d869d8b6b90c34ee0a462ce243012bc21dda460ce758b4cf7716de2fa'
family.CASES = {'nested-self-copy': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'nested-self-copy': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
