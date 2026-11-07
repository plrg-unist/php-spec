#!/usr/bin/env python3
"""COW deletion unwraps a singleton owning alias without deleting the old payload."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc79_singleton_alias_unset.php'
family.CASES = {'singleton-owning-alias-cow-deletion': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'singleton-owning-alias-cow-deletion': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
