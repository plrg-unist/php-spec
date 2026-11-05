#!/usr/bin/env python3
"""Native-first declared property order and bounded direct Child cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'declared-child-order-and-float': ROOT / 'tests/semantics/gc42_declared_child_order.php',
    'extra-null-declared-property': ROOT / 'tests/semantics/gc41_peer_extra_slot_boundary.php',
    'typed-property-boundary': ROOT / 'tests/semantics/gc42_typed_property_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 180 for name in SOURCES}
family.BASELINE = ('multiple-entry WeakMap storage destruction', b'B|1.25|')
family.UNSUPPORTED = {
    'typed-property-boundary': ('multiple-entry WeakMap storage destruction', b'B|'),
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
