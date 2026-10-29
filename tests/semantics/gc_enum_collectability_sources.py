#!/usr/bin/env python3
"""Native-first enum case GC-buffer status and ordinary-cycle control."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'case-and-ordinary-cycle': ROOT / 'tests/semantics/gc_enum_collectability_source.php',
    'case-buffer-status': ROOT / 'tests/semantics/gc_enum_collectability_status.php',
}
family.CASES = {name: path.read_bytes() for name, path in FILES.items()}
family.UNSUPPORTED = {}
family.BASELINE = ('gc_status is outside the modeled core intrinsics', b'Z|')
family.MODEL_TIMEOUTS = {'case-and-ordinary-cycle': 120}
EXPECTED_SHA256 = {
    'case-and-ordinary-cycle': '7f159522da3832a851378c8be5404cafe331f75e49780fb7bff00101da049399',
    'case-buffer-status': '07a53bc7d171a1b1abd75a5cf9e204db5dce823d92c932c5e3270f7f7f9a131b',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256


family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(path.relative_to(ROOT)): family.sha(path)
        for path in [*FILES.values(), Path(__file__)]})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
