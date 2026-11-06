#!/usr/bin/env python3
"""Own weak-live precedes retired property-array Child jobs and later Root slots."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc67_own_array_children.php'
source = SOURCE.read_bytes()
family.CASES = {
    'own-array-children-normal': source,
    'own-array-children-fresh': source.replace(
        b'$throw67 = false;', b'$throw67 = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
