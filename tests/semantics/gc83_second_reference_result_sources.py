#!/usr/bin/env python3
"""A second unused reference binding adds only its real CV owner."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc83_second_reference_result.php'
family.CASES = {'second-unused-reference-result': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'second-unused-reference-result': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
