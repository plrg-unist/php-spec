#!/usr/bin/env python3
"""Native-first observer order and fast-header shielding at executor shutdown."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'observer-lower': ('gc_inactive_weak_observer_lower_source.php',
        '1ba585483a058a116636a773a1587f35eecace6826b5efa034a0b4a779a86fe1'),
    'observer-higher': ('gc_inactive_weak_observer_higher_source.php',
        '5bfe37ea5cc4be915e57b509304293e382d560e358d59327bde6f2119a080aef'),
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, (filename, _) in FILES.items()}
for name, (_, expected) in FILES.items():
    assert hashlib.sha256(PATHS[name].read_bytes()).hexdigest() == expected
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {}
family.BASELINE = ('inactive executor storage hook or destructor visibility', b'FX|D1|L|D2|')
family.MODEL_TIMEOUTS = {name: 240 for name in FILES}
family.MODEL_STATUSES = {'observer-lower': 'php_error'}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
