#!/usr/bin/env python3
"""Unused third alias and genuine CV release retain distinct decrement laws."""
from pathlib import Path
import global_constant_sources as family

ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/gc83_third_reference_result.php'
family.CASES = {'unused-third-alias-and-real-release': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'unused-third-alias-and-real-release': 360}
original_fingerprint = family.fingerprint


def fingerprint():
    return dict(original_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
