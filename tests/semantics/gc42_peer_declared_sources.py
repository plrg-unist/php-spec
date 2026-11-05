#!/usr/bin/env python3
"""Independent declared-slot order, repeated Child and pending-throw cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc42_peer_declared_shared_throw.php'
family.CASES = {'declared-order-shared-child-throw': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'declared-order-shared-child-throw': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
