#!/usr/bin/env python3
"""Native-first rooted Closure captures with nested direct array DAGs."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'nested-shared-dag': ('gc_nested_array_dag_source.php',
        '5f77d8c4ece47886f6894bd1133744e1e657852d18910b2d9eef0cc39323a9b0'),
    'nested-local-cow': ('gc_nested_array_cow_source.php',
        '61eec52ca406248e8cb4715ef08ceae423af14ecff5b8f376452ee686918f5b5'),
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, (filename, _) in FILES.items()}
for name, (_, expected) in FILES.items():
    assert hashlib.sha256(PATHS[name].read_bytes()).hexdigest() == expected

family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {}
family.BASELINE = ('cached ordinary property-table collection', b'T|P|0|')
family.MODEL_TIMEOUTS = {name: 240 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
