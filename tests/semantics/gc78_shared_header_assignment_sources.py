#!/usr/bin/env python3
"""An extra real old-array CV survives native-count separation."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc78_shared_header_assignment.php'
family.CASES = {'shared-header-assignment-and-real-old-view-release': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-header-assignment-and-real-old-view-release': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
