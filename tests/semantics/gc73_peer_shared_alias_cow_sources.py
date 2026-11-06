#!/usr/bin/env python3
"""COW preserves a repeated shared scalar reference under an old count unit."""
from pathlib import Path

import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc73_peer_shared_alias_cow.php'
family.CASES = {'shared-scalar-alias-native-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-scalar-alias-native-cow': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint

if __name__ == '__main__':
    family.main()
