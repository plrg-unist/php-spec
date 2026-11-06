#!/usr/bin/env python3
"""Shared DIRECT-array DAG copies retain physical descendant multiplicity."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc66_peer_shared_array_read.php'
source = SOURCE.read_bytes()
family.CASES = {
    'shared-array-normal': source,
    'shared-array-fresh-throw': source.replace(
        b'$throw66Peer = false;', b'$throw66Peer = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
