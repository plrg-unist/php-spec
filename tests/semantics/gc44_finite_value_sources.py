#!/usr/bin/env python3
"""Native-first prebuilt finite payload insertion/append and unchanged boundaries."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCES = {
    'prebuilt-value-insert-and-append': ROOT / 'tests/semantics/gc44_prebuilt_value_insertion.php',
    'occupied-replacement-boundary': ROOT / 'tests/semantics/gc37_value_child_occupied_replacement.php',
    'shared-key-payload-boundary': ROOT / 'tests/semantics/gc44_shared_key_payload_boundary.php',
}
family.CASES = {name: path.read_bytes() for name, path in SOURCES.items()}
family.MODEL_TIMEOUTS = {name: 240 for name in SOURCES}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'B|')
family.UNSUPPORTED = {name: ('WeakMap dimension protocol outside first insertion', b'B|')
                      for name in ['occupied-replacement-boundary', 'shared-key-payload-boundary']}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*SOURCES.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
