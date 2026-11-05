#!/usr/bin/env python3
"""Native-first observer order and fast-header shielding at executor shutdown."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'observer-lower': ('gc_inactive_weak_observer_lower_source.php',
        '80e135c74c4abf2a2f222e486a2a9eac7b08394353656bdb678ef4a853541364'),
    'observer-higher': ('gc_inactive_weak_observer_higher_source.php',
        'f7ebe9a9988324a72f57ba1d35938b6bd1f26ed5416296ace612afa79e649834'),
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
