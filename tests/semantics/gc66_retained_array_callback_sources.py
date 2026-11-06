#!/usr/bin/env python3
"""Retained incoming array owners through own/Child reads and explicit CV drops."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc66_retained_array_callback.php'
source = SOURCE.read_bytes()
family.CASES = {
    'retained-array-callback-normal': source,
    'retained-array-callback-fresh': source.replace(
        b'$throw66 = false;', b'$throw66 = true;'),
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
