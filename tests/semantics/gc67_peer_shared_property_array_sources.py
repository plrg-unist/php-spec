#!/usr/bin/env python3
"""Shared Root arrays release repeated Children once, before later Root slots."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc67_peer_shared_property_array.php'
source = SOURCE.read_bytes()
family.CASES = {
    'shared-property-array-normal': source,
    'shared-property-array-fresh-own': source.replace(
        b'$throwOwn67Peer = false;', b'$throwOwn67Peer = true;'),
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
