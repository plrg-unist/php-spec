#!/usr/bin/env python3
"""Own weak-live read precedes ordered Middle/shared-Child cleanup and NULL reads."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc63_peer_shared_own_slots.php'
source = SOURCE.read_bytes()
family.CASES = {
    'shared-own-slots-present-null-normal': source,
    'shared-own-slots-present-null-fresh-throw': source.replace(
        b'$throw63Peer = false;', b'$throw63Peer = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
