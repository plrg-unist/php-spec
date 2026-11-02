#!/usr/bin/env python3
"""Pinned shared array/leaf Closure capture and native root-status control."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'shared-array-leaf': ('gc_shared_capture_source.php',
        'a5dbab7bc68a197ce290df1ee455aaaf4893229a1ad7c13e59b9527852c5a0d3'),
    'shared-leaf-array-reversed': ('gc_shared_capture_reversed_source.php',
        'bd703ad07bc889f6ed2701c44445c47c923913d8e3a68703eb41f8583b5b03e5'),
    'native-shared-status': ('gc_shared_capture_status.php',
        '287a9e65b4ec9d9fc9a35093b1382e050e3e409680d2022e5c3c2e721924c461'),
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, (filename, _) in FILES.items()}
for name, (_, expected) in FILES.items():
    assert hashlib.sha256(PATHS[name].read_bytes()).hexdigest() == expected

family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'shared-array-leaf': 240, 'shared-leaf-array-reversed': 240}


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
