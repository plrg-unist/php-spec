#!/usr/bin/env python3
"""Independent finite Key-death cleanup with both weak registration orders."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'key-before-shared-property-cleanup': ROOT / 'tests/semantics/gc45_peer_key_before_shared_fields.php',
    'key-after-throwing-property-cleanup': ROOT / 'tests/semantics/gc45_peer_key_after_throw.php',
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
