#!/usr/bin/env python3
"""Independent held old Value and finite incoming payload replacement."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc48_peer_held_old_replacement.php'
family.CASES = {'replacement-held-old-and-new-child': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'replacement-held-old-and-new-child': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
