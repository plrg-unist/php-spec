#!/usr/bin/env python3
"""Repeated inner HARRAY edges delay nested payload cleanup through a throw."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc55_peer_shared_inner_array_throw.php'
family.CASES = {'nested-root-shared-inner-child-throw': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'nested-root-shared-inner-child-throw': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
