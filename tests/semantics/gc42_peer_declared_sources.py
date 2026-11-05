#!/usr/bin/env python3
"""Independent declared-slot order, repeated Child and pending-throw cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'declared-order-shared-child-throw': ROOT / 'tests/semantics/gc42_peer_declared_shared_throw.php',
    'deeper-object-boundary': ROOT / 'tests/semantics/gc42_peer_deeper_object_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 240 for name in SOURCES}
family.UNSUPPORTED = {
    'deeper-object-boundary': ('multiple-entry WeakMap storage destruction', b'B|'),
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
