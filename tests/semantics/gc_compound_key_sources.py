#!/usr/bin/env python3
"""Native-first internal weak-Key cleanup phases and ordinary retirement fences."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'weak-key-field-shield': 'gc_compound_weak_key_fast_source.php',
    'weak-key-incoming': 'gc_compound_weak_key_notify_source.php',
    'map-key-own-before-incoming': 'gc_compound_map_key_order_source.php',
    'map-key-held-own': 'gc_compound_map_key_held_source.php',
    'map-key-shared-value': 'gc_compound_map_key_shared_source.php',
    'map-key-self': 'gc_compound_map_key_self_source.php',
    'map-key-multi-shared': 'gc_compound_map_key_multi_source.php',
    'map-key-cross-shared': 'gc_compound_map_key_cross_source.php',
    'ordinary-weak-key': 'gc_compound_weak_key_unset_control.php',
    'ordinary-map-key': 'gc_compound_map_key_unset_control.php',
    'ordinary-nonempty-map-key': 'gc_compound_map_nonempty_unset_control.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'FX|D1|')
family.UNSUPPORTED = {name: ('ordinary internal weak-key notification', b'B|')
                      for name in ['ordinary-weak-key', 'ordinary-map-key',
                                   'ordinary-nonempty-map-key']}
family.MODEL_STATUSES = {name: 'php_error' for name in [
    'weak-key-incoming', 'map-key-own-before-incoming', 'map-key-held-own']}
family.MODEL_TIMEOUTS = {name: 240 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
