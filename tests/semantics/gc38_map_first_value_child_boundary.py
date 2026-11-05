#!/usr/bin/env python3
"""Outside Child ownership keeps Map-first Value retirement bounded."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc38_map_first_retained_child.php'
family.CASES = {'retained-child-unsupported': SOURCE.read_bytes()}
family.UNSUPPORTED = {'retained-child-unsupported':
    ('nonempty WeakMap storage destruction', b'B|')}
family.MODEL_TIMEOUTS = {'retained-child-unsupported': 120}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
