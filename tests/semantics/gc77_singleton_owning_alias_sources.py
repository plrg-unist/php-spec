#!/usr/bin/env python3
"""Owning singleton ALIAS unwraps while the hidden old array keeps Child."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc77_singleton_owning_alias.php'
family.CASES = {'singleton-owning-alias-retained-cow': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'singleton-owning-alias-retained-cow': 360}
family.BASELINE = ('is_callable output rebound to owning value or new type source', b'B|O|')
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
