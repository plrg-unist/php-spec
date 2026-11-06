#!/usr/bin/env python3
"""A unique empty cast temporary compares with a nonempty scalar array literal."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc61_peer_cast_temp_identity.php'
family.CASES = {'empty-cast-nonidentity-two-temporaries': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
