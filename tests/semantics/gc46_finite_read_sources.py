#!/usr/bin/env python3
"""Finite Map reads create strong owners; terminal presence reads borrow storage."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'direct-fetched-retained-child-throw': ROOT / 'tests/semantics/gc46_direct_fetched_retained.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 240 for name in SOURCES}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
