#!/usr/bin/env python3
"""A hidden native-retained Parent keeps array-copy reference owners real."""
from pathlib import Path
import global_constant_sources as family
ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc70_cow_hidden_reference.php'
family.CASES = {'cow-hidden-reference': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'cow-hidden-reference': 360}
original_fingerprint = family.fingerprint
def fingerprint():
    return dict(original_fingerprint(), **{str(path.relative_to(ROOT)):family.sha(path) for path in [SOURCE,Path(__file__)]})
family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
