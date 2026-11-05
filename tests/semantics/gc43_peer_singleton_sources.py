#!/usr/bin/env python3
"""Singleton finite-field cleanup and concrete compatibility boundaries."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'singleton-retained-value-fields': ROOT / 'tests/semantics/gc43_peer_retained_fields.php',
    'many-backed-getter-no-dispatch': ROOT / 'tests/semantics/gc43_peer_many_backed_getter.php',
    'affected-leaf-incoming-notice': ROOT / 'tests/semantics/gc_ordinary_review_map_own_phase_global.php',
    'incoming-child-boundary': ROOT / 'tests/semantics/gc38_map_first_incoming_key.php',
    'virtual-property-boundary': ROOT / 'tests/semantics/gc43_peer_virtual_property_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 240 for name in SOURCES}
family.UNSUPPORTED = {
    'incoming-child-boundary': ('nonempty WeakMap storage destruction', b'B|'),
    'virtual-property-boundary': ('multiple-entry WeakMap storage destruction', b'B|'),
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
