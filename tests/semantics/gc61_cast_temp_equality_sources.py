#!/usr/bin/env python3
"""Generic temporary queue consumption through an ordinary empty-class cast."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc61_cast_temp_equality.php'
family.CASES = {'cast-empty-equality': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'cast-empty-equality': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
