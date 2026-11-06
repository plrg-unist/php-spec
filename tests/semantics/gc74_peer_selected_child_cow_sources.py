#!/usr/bin/env python3
"""Only the overwritten copied Child decrements during retained-array COW."""
from pathlib import Path

import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc74_peer_selected_child_cow.php'
family.CASES = {'selected-child-copy-and-untouched-siblings': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'selected-child-copy-and-untouched-siblings': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
