#!/usr/bin/env python3
"""A shared Child replaces the own pending exception before later slot cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc64_peer_shared_throw_slots.php'
family.CASES = {'shared-child-fresh-over-own-pending-null': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
