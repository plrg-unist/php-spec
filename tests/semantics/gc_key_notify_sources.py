#!/usr/bin/env python3
"""Inactive standard-Key notification precedes fields and releases one entry."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'notify-before-fields': 'gc_inactive_weakmap_key_notify_source.php',
    'retained-value-before-field': 'gc_inactive_weakmap_key_field_source.php',
    'registration-order': 'gc_key_notify_order_source.php',
    'shared-reference-value': 'gc_key_notify_alias_source.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.BASELINE = ('inactive executor storage hook or destructor visibility', b'FX|D1|D2|')
family.UNSUPPORTED = {}
family.MODEL_STATUSES = {name: 'php_error' for name in FILES if name != 'shared-reference-value'}
family.MODEL_TIMEOUTS = {name: 240 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
