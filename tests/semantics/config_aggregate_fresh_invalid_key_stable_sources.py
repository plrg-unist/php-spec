#!/usr/bin/env python3
"""A fresh Iterator from a live Aggregate with only its source CV owner."""
from pathlib import Path

import config_aggregate_fresh_invalid_key_sources as sources


family = sources.family
name = 'unheld-stable-null-first-key'
family.CASES = {name: sources.source(
    br'$key0 = null; $key1 = 1; $rebindAt = -1;', sources.ERROR_CALL, held=False)}
family.UNSUPPORTED = {}
family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
