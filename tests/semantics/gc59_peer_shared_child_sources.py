#!/usr/bin/env python3
"""Two old property owners reach one read-only current-row Child callback."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc59_peer_shared_child_read.php'
source = SOURCE.read_bytes()
family.CASES = {
    'shared-child-current-row-read-normal': source,
    'shared-child-current-row-read-fresh-throw': source.replace(
        b'$throw59Peer = false;', b'$throw59Peer = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'B|s|17|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
