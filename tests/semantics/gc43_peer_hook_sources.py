#!/usr/bin/env python3
"""Compatibility seam for singleton retirement of an existing backed getter."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc43_peer_backed_get_only.php'
family.CASES = {'singleton-backed-getter': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'singleton-backed-getter': 180}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
