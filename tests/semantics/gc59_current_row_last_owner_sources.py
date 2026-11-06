#!/usr/bin/env python3
"""Current-row last-owner Child reads publication before return/fresh throw."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc59_current_row_last_owner.php'
source = SOURCE.read_bytes()
family.CASES = {
    'current-last-owner-child-read-normal': source,
    'current-last-owner-child-read-fresh-throw': source.replace(
        b'$throw59 = false;', b'$throw59 = true;'),
}
family.MODEL_TIMEOUTS = {name: 360 for name in family.CASES}
family.BASELINE = ('WeakMap multiple-entry dimension protocol', b'B|')
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
