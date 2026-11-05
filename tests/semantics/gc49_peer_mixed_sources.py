#!/usr/bin/env python3
"""Independent mixed scalar/object replacement and selective Key retirement."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc49_peer_mixed_retained.php'
family.CASES = {'mixed-retained-object-to-scalar': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'mixed-retained-object-to-scalar': 300}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
