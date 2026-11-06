#!/usr/bin/env python3
"""Direct old Value destruction keeps its weak referent live before a NULL read."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc62_peer_null_own_read.php'
source = SOURCE.read_bytes()
family.CASES = {
    'own-dtor-present-null-normal': source,
    'own-dtor-present-null-fresh-throw': source.replace(
        b'$throw62Peer = false;', b'$throw62Peer = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family.BASELINE = ('WeakMap foreach mode, targets, or storage', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
