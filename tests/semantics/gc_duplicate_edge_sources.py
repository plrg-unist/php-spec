#!/usr/bin/env python3
"""Pinned duplicate-edge Closure lifetime source and native status control."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'duplicate-retained-only': ('gc_duplicate_edge_retained_source.php',
        '04d349d493cba4b83fcf7bd3ced2eb5f5b26ad15a6a5aeeeb6286a4ec54c4fed'),
    'native-duplicate-status': ('gc_duplicate_edge_retained_status.php',
        '5324972fd310c563e5b6138aad4fa6288f81aa5138ca98675381aac3a9f35b90'),
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, (filename, _) in FILES.items()}
for name, (_, expected) in FILES.items():
    assert hashlib.sha256(PATHS[name].read_bytes()).hexdigest() == expected

family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {
    'duplicate-retained-only': ('cached ordinary property-table collection', b'T|P|0|'),
}
family.MODEL_TIMEOUTS = {'duplicate-retained-only': 240}


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
