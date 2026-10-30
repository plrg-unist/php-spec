#!/usr/bin/env python3
"""Native-first materialized collection from a real Closure caller."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc_closure_caller_source.php'
family.CASES = {'real-closure-caller': SOURCE.read_bytes()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'real-closure-caller': 240}
EXPECTED_SHA256 = '4a80b8bbcf250c9c27b08ef8893e565acee0f2909b6317a972fc55f36274f47a'
assert hashlib.sha256(family.CASES['real-closure-caller']).hexdigest() == EXPECTED_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
