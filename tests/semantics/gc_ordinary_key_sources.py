#!/usr/bin/env python3
"""Native-first ordinary internal weak-Key storage retirement."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'weak-key-unset': 'gc_compound_weak_key_unset_control.php',
    'empty-map-key-unset': 'gc_compound_map_key_unset_control.php',
    'nonempty-map-key-unset': 'gc_compound_map_nonempty_unset_control.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.BASELINE = ('ordinary internal weak-key notification', b'B|')
family.MODEL_TIMEOUTS = {name: 120 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
