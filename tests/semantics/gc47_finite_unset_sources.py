#!/usr/bin/env python3
"""Explicit finite entry removal preserves selected-Key and abrupt cleanup order."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'selected-key-unset-child-throw': ROOT / 'tests/semantics/gc47_unset_selected_key_throw.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 240 for name in SOURCES}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'B|K|1|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
