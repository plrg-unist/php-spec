#!/usr/bin/env python3
"""Independent cloned payload and abrupt key evaluation from original bytes."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'clone-prebuilt-first-insertion': ROOT / 'tests/semantics/gc44_peer_clone_prebuilt.php',
    'key-throw-before-clone-consumption': ROOT / 'tests/semantics/gc44_peer_key_throw_clone.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 240 for name in SOURCES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
