#!/usr/bin/env python3
"""Current-Key scalar/array reads retain a separate result through loop retirement."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc57_peer_current_key_dag_read.php'
family.CASES = {'current-key-scalar-and-dag-read': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'current-key-scalar-and-dag-read': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
