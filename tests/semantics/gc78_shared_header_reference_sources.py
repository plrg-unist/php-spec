#!/usr/bin/env python3
"""Reference acquisition preserves a real old-array CV owner."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc78_shared_header_reference.php'
family.CASES = {'shared-header-reference-acquisition': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-header-reference-acquisition': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
