#!/usr/bin/env python3
"""Native-first Key notification probes for selective WeakMap value release."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'selective': ('gc_key_notify_selective_source.php',
        '2268e597b707f5bf4cbf22f81ac10e3c984359e60f30cd916d9cc9242a48deef'),
    'shared-value': ('gc_key_notify_shared_value_source.php',
        'b70a195dc57ef4f43e55bf465e314dca6f76be03ef76d29a193c9dc403d7982e'),
    'nested': ('gc_key_notify_nested_source.php',
        'd88cb2b8a995c7d92afd2443291da7a0d2b6e447705f63c1eb3dcd15fa4c0390'),
    'late-slot': ('gc_key_notify_late_slot_source.php',
        '83529b08a5ff1f4ea8cd48019becf5fd3346d3f8a98534beef57bb49ee663b9f'),
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, (filename, _) in FILES.items()}
for name, (_, expected) in FILES.items():
    assert hashlib.sha256(PATHS[name].read_bytes()).hexdigest() == expected
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {}
family.MODEL_STATUSES = {name: 'php_error' for name in FILES}
family.MODEL_TIMEOUTS = {name: 240 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
