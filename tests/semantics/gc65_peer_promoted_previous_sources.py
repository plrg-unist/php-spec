#!/usr/bin/env python3
"""Fresh C replaces pending B whose physical Previous is the own Exception A."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc65_peer_promoted_previous_chain.php'
family.CASES = {'later-child-fresh-over-established-previous': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
fingerprint_base = family.fingerprint


def fingerprint():
    return dict(fingerprint_base(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
