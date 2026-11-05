#!/usr/bin/env python3
"""Independent finite quiet result ownership and absent-Key consumers."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc46_peer_quiet_missing_retained.php'
family.CASES = {'quiet-missing-and-retained-result': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'quiet-missing-and-retained-result': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
