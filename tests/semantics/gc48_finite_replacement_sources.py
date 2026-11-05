#!/usr/bin/env python3
"""Occupied singleton publication precedes supplied/fresh Child throws."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc48_replacement_child_throw.php'
source = SOURCE.read_bytes()
family.CASES = {
    'singleton-replacement-supplied-child-throw': source,
    'singleton-replacement-fresh-child-throw': source.replace(
        b'$fresh = false;', b'$fresh = true;'),
}
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
