#!/usr/bin/env python3
"""Native-first inactive Map unregister and ordered owning-value release."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'map-held-value': ('gc_inactive_weakmap_held_source.php',
        'b9812cfd9dbbd1a5b02dae13b4592af9de8e1736861aa58407212fd3a92f9650'),
    'map-values-ab': ('gc_inactive_weakmap_ab_source.php',
        'f9ce08a777f40f4aac4869eef412f79c099970149af5d45cf95ef427ee88b7c3'),
    'map-values-ba': ('gc_inactive_weakmap_ba_source.php',
        '3477eec1ef1dc3b70617c359f25f41fd6d255ed6a82b9f21c91609455a5bf1e3'),
    'map-alias-empty': ('gc_inactive_weakmap_alias_source.php',
        'c9545e0a2a86e3c830380727216efde07e5e7c0a4868a3baf4a20d8e6187481c'),
    'key-notify-before-fields': ('gc_inactive_weakmap_key_notify_source.php',
        '031031b64f89f54e5d778af80480411546d5cec7b2536c96a14f5477d84fccbd'),
    'key-before-map-field': ('gc_inactive_weakmap_key_field_source.php',
        '5e5638611b7451779811f94dbd93291f3dad110ce731a06cc4b0998a606c7b25'),
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, (filename, _) in FILES.items()}
for name, (_, expected) in FILES.items():
    assert hashlib.sha256(PATHS[name].read_bytes()).hexdigest() == expected
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.BASELINE = ('inactive executor storage hook or destructor visibility', b'FX|D1|D2|')
family.UNSUPPORTED = {name: family.BASELINE for name in ['key-notify-before-fields', 'key-before-map-field']}
family.MODEL_STATUSES = {'map-values-ab': 'php_error', 'map-values-ba': 'php_error'}
family.MODEL_TIMEOUTS = {name: 240 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
