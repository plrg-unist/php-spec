#!/usr/bin/env python3
"""Retain the selected public NaN property through API error argument delivery."""
from pathlib import Path

import global_constant_sources as family


ROOT = family.ROOT
SOURCE = ROOT / 'tests/semantics/quiet-public-nan-one-default.php'
family.CASES = {'property-nan-one-default-api-handler': SOURCE.read_bytes()}
family.MODEL_TIMEOUTS = {'property-nan-one-default-api-handler': 180}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [SOURCE, Path(__file__)]})


family.fingerprint = fingerprint
if __name__ == '__main__':
    family.main()
