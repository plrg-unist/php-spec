#!/usr/bin/env python3
"""Two old declared edges release one Child that reads the present NULL row."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc60_peer_null_current_read.php'
source = SOURCE.read_bytes()
family.CASES = {
    'shared-child-current-null-read-normal': source,
    'shared-child-current-null-read-fresh-throw': source.replace(
        b'$throw60Peer = false;', b'$throw60Peer = true;'),
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
