#!/usr/bin/env python3
"""Independent Map-first declared Value child source pairs."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'key-wrapper-before-map-entry': 'gc38_peer_map_first_observers.php',
    'caught-child-throw': 'gc38_peer_map_first_throw.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {name: 120 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
