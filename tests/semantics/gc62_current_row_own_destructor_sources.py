#!/usr/bin/env python3
"""Current-row old root remains weakly live through its own destructor."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc62_current_row_own_destructor.php'
source = SOURCE.read_bytes()
family.CASES = {
    'current-own-destructor-read-normal': source,
    'current-own-destructor-read-fresh-throw': source.replace(
        b'$throw62 = false;', b'$throw62 = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family.BASELINE = ('WeakMap foreach mode, targets, or storage', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
