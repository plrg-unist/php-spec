#!/usr/bin/env python3
"""KEY_R copies from the current finite row outlive foreach Value and Map CVs."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc57_foreach_current_object_read.php'
family.CASES = {'current-object-read-survives-loop-value-map': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'current-object-read-survives-loop-value-map': 360}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
