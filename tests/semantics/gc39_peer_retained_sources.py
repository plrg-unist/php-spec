#!/usr/bin/env python3
"""Independent retained Child source and exact owner-three refusal."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'caught-deferred-child-throw': 'gc39_peer_retained_throw.php',
    'owner-three-boundary': 'gc39_peer_owner3_boundary.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {'owner-three-boundary': ('nonempty WeakMap storage destruction', b'B|')}
family.MODEL_TIMEOUTS = {name: 180 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
