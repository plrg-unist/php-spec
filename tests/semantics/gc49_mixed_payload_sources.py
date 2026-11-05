#!/usr/bin/env python3
"""Mixed scalar/finite tables share replacement and ordinary storage consumers."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'scalar-to-finite-mixed-map-free': ROOT / 'tests/semantics/gc49_scalar_to_finite_mixed_free.php',
    'finite-to-null-child-throw': ROOT / 'tests/semantics/gc49_finite_to_null_throw.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 300 for name in SOURCES}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
