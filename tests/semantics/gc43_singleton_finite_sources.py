#!/usr/bin/env python3
"""Native-first singleton finite property cleanup and retained-owner promotion."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'singleton-declared-child-throw': ROOT / 'tests/semantics/gc43_singleton_declared_throw.php',
    'singleton-child-owner-three': ROOT / 'tests/semantics/gc39_peer_owner3_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 180 for name in SOURCES}
family.BASELINE = ('nonempty WeakMap storage destruction', b'B|Q|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
