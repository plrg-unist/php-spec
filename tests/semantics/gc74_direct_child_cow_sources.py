#!/usr/bin/env python3
"""Copied DIRECT Child decrements before retained old-header shutdown."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc74_direct_child_cow.php'
family.CASES = {'direct-child-copy-drop': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'direct-child-copy-drop': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
