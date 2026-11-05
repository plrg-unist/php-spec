#!/usr/bin/env python3
"""Independent finite Map free with later callbacks and shared retained owners."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'four-entry-first-child-throw': ROOT / 'tests/semantics/gc41_peer_many_children_throw.php',
    'duplicate-value-shared-retained-child': ROOT / 'tests/semantics/gc41_peer_shared_retained_value.php',
    'extra-declared-slot-boundary': ROOT / 'tests/semantics/gc41_peer_extra_slot_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 180 for name in SOURCES}
family.UNSUPPORTED = {
    'extra-declared-slot-boundary': ('multiple-entry WeakMap storage destruction', b'B|'),
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
