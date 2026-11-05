#!/usr/bin/env python3
"""Native-first finite direct Map teardown and promoted two-Child case."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'four-entry-child-order': ROOT / 'tests/semantics/gc41_four_entry_child_order.php',
    'two-declared-child-values': ROOT / 'tests/semantics/gc40_peer_two_fields_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 180 for name in SOURCES}
family.BASELINE = ('multiple-entry WeakMap storage destruction', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
