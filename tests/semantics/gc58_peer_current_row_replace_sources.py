#!/usr/bin/env python3
"""Current-row scalar/array replacement preserves the copied old loop value."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc58_peer_current_row_dag_replace.php'
family.CASES = {'current-row-scalar-and-dag-replacement': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'current-row-scalar-and-dag-replacement': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
