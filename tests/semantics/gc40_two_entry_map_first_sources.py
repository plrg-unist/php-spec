#!/usr/bin/env python3
"""Native-first two-entry Map teardown with one declared-child Value."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc40_first_field_second_leaf.php'
family.CASES = {'field-first-leaf-second': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'field-first-leaf-second': 150}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
