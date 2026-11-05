#!/usr/bin/env python3
"""Independent standard weak-Key child and observer-order sources."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'child-preinsert': 'gc36_key_child_preinsert.php',
    'child-postinsert': 'gc36_key_child_postinsert.php',
    'observer-first': 'gc36_key_child_observer_first.php',
    'value-throws': 'gc36_key_child_value_throw.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.MODEL_TIMEOUTS = {name: 180 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
