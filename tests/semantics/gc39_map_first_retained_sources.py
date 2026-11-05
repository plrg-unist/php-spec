#!/usr/bin/env python3
"""Native-first Map teardown with one externally retained Value child."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc39_map_first_retained_observers.php'
family.CASES = {'map-first-retained-child': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'map-first-retained-child': 120}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
