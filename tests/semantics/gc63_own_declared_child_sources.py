#!/usr/bin/env python3
"""Old own callback precedes weak notification and declared Child release."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc63_own_declared_child.php'
source = SOURCE.read_bytes()
family.CASES = {
    'own-declared-child-normal': source,
    'own-declared-child-fresh-throw': source.replace(
        b'$throw63 = false;', b'$throw63 = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
