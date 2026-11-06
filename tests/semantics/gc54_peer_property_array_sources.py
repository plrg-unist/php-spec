#!/usr/bin/env python3
"""Declaration-order release of a shared property array through a Child throw."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc54_peer_shared_array_property_order.php'
family.CASES = {'shared-property-array-order-throw': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-property-array-order-throw': 360}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
