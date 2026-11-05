#!/usr/bin/env python3
"""Native-first first insertion of a WeakMap Value with one declared child."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'child-before-insertion': 'gc37_value_child_preinsert.php',
    'child-after-insertion-control': 'gc37_value_child_postinsert.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.MODEL_TIMEOUTS = {name: 120 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
