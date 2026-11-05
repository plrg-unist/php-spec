#!/usr/bin/env python3
"""Independent ordinary weak-Key callback and throw source probes."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'wr-recreate-in-incoming': 'gc_ordinary_review_wr_recreate_in_incoming.php',
    'wr-recreate-global': 'gc_ordinary_review_wr_recreate_global.php',
    'map-own-phase-weak-visibility': 'gc_ordinary_review_map_own_phase_weak_visibility.php',
    'map-own-phase-global': 'gc_ordinary_review_map_own_phase_global.php',
    'map-own-throw-suffix': 'gc_ordinary_review_map_own_throw_suffix.php',
    'wr-incoming-throw-suffix': 'gc_ordinary_review_wr_incoming_throw_suffix.php',
    'wr-single-throw': 'gc_ordinary_review_wr_single_throw.php',
}
PATHS = {name: ROOT / 'tests/semantics' / filename for name, filename in FILES.items()}
family.CASES = {name: path.read_bytes() for name, path in PATHS.items()}
family.BASELINE = ('ordinary internal weak-key notification', b'B|')
family.MODEL_TIMEOUTS = {name: 180 for name in FILES}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*PATHS.values(), Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
