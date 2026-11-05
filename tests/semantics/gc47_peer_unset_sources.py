#!/usr/bin/env python3
"""Independent explicit slot removal with a fetched owner and live siblings."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc47_peer_unset_retained_value.php'
family.CASES = {'unset-retained-value-entry-absence': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'unset-retained-value-entry-absence': 240}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
