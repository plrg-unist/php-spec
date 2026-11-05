#!/usr/bin/env python3
"""Native-first Map retirement of an owned declared-child Value."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc38_map_first_value_child.php'
family.CASES = {'map-first-declared-child': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'map-first-declared-child': 120}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
