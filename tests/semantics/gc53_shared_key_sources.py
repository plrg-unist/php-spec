#!/usr/bin/env python3
"""One ordinary shared Key releases two real Value owners in registration order."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc53_shared_object_key_death.php'
family.CASES = {'shared-object-key-death-early-wrapper-throw': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'shared-object-key-death-early-wrapper-throw': 300}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
