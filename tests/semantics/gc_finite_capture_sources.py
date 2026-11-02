#!/usr/bin/env python3
"""Native-first finite Closure capture/array graph controls."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'finite-reversed-captures': ('gc_finite_reversed_scalar_array.php',
        'cca7681ec5bc033216ab17bd2f641e685ec2b13bc61690e8654f58c24949636b'),
    'finite-three-distinct-mixed-key': ('gc_finite_three_distinct_mixed_key.php',
        '33184290cbbbac695d37c9c3521eb0eb84455defc926fcab77c6d080d112ca3b'),
    'finite-duplicate-child': ('gc_finite_duplicate_array_child.php',
        'b5a3f6a19ec336778ca8b3c1a76e3512748cd9b1af0d0a6c16b320b1a2ddf867'),
    'finite-cow-after-capture': ('gc_finite_cow_after_array_capture.php',
        'cc28bb6dd161466e6d513d341f83678ab50f9dca47b256d2f98f5e79ec988b8e'),
    'native-finite-reversed-capture-order': ('gc_finite_reversed_capture_order.php',
        '12047d23c1489ea21944dd8fb9e19b766866410ba8510e30388fa094677fd6dc'),
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, (filename, _) in FILES.items()}
for name, (_, expected) in FILES.items():
    assert hashlib.sha256(PATHS[name].read_bytes()).hexdigest() == expected

family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.UNSUPPORTED = {
    'finite-duplicate-child': ('cached ordinary property-table collection', b'T|P|0|'),
}
family.MODEL_TIMEOUTS = {name: 240 for name in FILES if not name.startswith('native-')}


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
