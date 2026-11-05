#!/usr/bin/env python3
"""Native-first ordinary reference captures, payload sharing and name rebinding."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'shared-cell': ('gc_reference_capture_shared_cell_source.php',
        'ccf48b3084c8265201f69e21bc6157f156afa22f6923b57deab148acf73b92af'),
    'distinct-cells': ('gc_reference_capture_distinct_cells_source.php',
        '151b12b4533c3fc12e3762253a54913b2e9c4be27b291b8c509249178858c411'),
    'request-string-rebind': ('gc_reference_capture_string_rebind_source.php',
        'd7e76f9982d6a097be0edf7d250e06fecadbe8c2d265f805ad5f9efe03b7eec8'),
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
