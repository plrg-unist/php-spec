#!/usr/bin/env python3
"""Unpack preserves a reference also owned by a native-retained Parent."""
from pathlib import Path
import global_constant_sources as family
ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc70_peer_unpack_reference.php'
family.CASES = {'unpack-keeps-parent-reference': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'unpack-keeps-parent-reference': 360}
original_fingerprint = family.fingerprint
def fingerprint():
    return dict(original_fingerprint(), **{str(path.relative_to(ROOT)):family.sha(path) for path in [SOURCE,Path(__file__)]})
family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
