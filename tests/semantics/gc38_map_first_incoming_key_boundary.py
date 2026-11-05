#!/usr/bin/env python3
"""An incoming Map key keeps declared-child Map free outside GC38."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc38_map_first_incoming_key.php'
family.CASES = {'incoming-map-key-unsupported': SOURCE.read_bytes()}
family.UNSUPPORTED = {'incoming-map-key-unsupported':
    ('nonempty WeakMap storage destruction', b'B|')}
family.MODEL_TIMEOUTS = {'incoming-map-key-unsupported': 120}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
