#!/usr/bin/env python3
"""Native-first finite multi-array Closure capture graphs and weak lifetime."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'distinct-shared': ('gc_multi_array_shared_source.php',
        'ebc400582beb5de62bdc376e8d9b11385d73b0b083aaa9ac7c22b27421c8cfc6'),
    'repeated-array': ('gc_multi_array_repeated_source.php',
        'bd172870ca8e5036475dadae239ac9cdc1695e3bc852696dc6941c98d884c745'),
    'three-reordered': ('gc_multi_array_three_source.php',
        '2ca46ea6b013a50cb874eb286c6bf79b6309b436c540dbb61faaa18e94740866'),
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
