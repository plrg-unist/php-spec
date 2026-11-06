#!/usr/bin/env python3
"""One nonowning primitive family through the real last-owner Child callback."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc60_current_row_quiet_scalar.php'
source = SOURCE.read_bytes()


def scalar_source(value):
    assert source.count(b'$incoming60 = 23;') == 1
    assert source.count(b'$expected60 = 23;') == 1
    return source.replace(b'$incoming60 = 23;', b'$incoming60 = ' + value + b';').replace(
        b'$expected60 = 23;', b'$expected60 = ' + value + b';')


family.CASES = {
    'quiet-int-normal': source,
    'quiet-int-fresh-throw': source.replace(b'$throw60 = false;', b'$throw60 = true;'),
    'quiet-false-normal': scalar_source(b'false'),
    'quiet-float-normal': scalar_source(b'1.25'),
    'quiet-literal-string-normal': scalar_source(b"'quiet'"),
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
