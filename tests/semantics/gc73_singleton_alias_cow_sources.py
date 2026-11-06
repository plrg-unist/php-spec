#!/usr/bin/env python3
"""Quiet singleton ALIAS unwraps in a native-retained array COW copy."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc73_singleton_alias_cow.php'
family.CASES = {'singleton-quiet-alias-array-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'singleton-quiet-alias-array-cow': 360}
family.BASELINE = ('is_callable output rebound to owning value or new type source', b'B|O|')
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
