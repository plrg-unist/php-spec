#!/usr/bin/env python3
"""Finite WeakMap foreach copies retain Map DATA and delivered Key/Value owners."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'finite-object-break-map-cv-release': ROOT / 'tests/semantics/gc56_foreach_object_break.php',
    'nested-array-break-map-cv-release': ROOT / 'tests/semantics/gc56_foreach_array_break.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 360 for name in SOURCES}
family.BASELINE = ('WeakMap foreach mode, targets, or storage', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
