#!/usr/bin/env python3
"""Ranked mixed-value traversal captures the last finite DAG payload until CV cleanup."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc56_peer_finite_foreach_exhaustion.php'
family.CASES = {'finite-foreach-ranked-exhaustion': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'finite-foreach-ranked-exhaustion': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
