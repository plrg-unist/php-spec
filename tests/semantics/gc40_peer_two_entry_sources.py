#!/usr/bin/env python3
"""Independent reverse cleanup, caught throw and explicit two-entry boundaries."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'leaf-first-field-second-throw': ROOT / 'tests/semantics/gc40_peer_reverse_throw.php',
    'two-declared-values-boundary': ROOT / 'tests/semantics/gc40_peer_two_fields_boundary.php',
    'nested-callback-presence-boundary': ROOT / 'tests/semantics/gc40_peer_presence_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 150 for name in SOURCES}
family.UNSUPPORTED = {
    'two-declared-values-boundary': ('multiple-entry WeakMap storage destruction', b'B|'),
    'nested-callback-presence-boundary': ('WeakMap dimension protocol outside first insertion', b'B|P|'),
}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
