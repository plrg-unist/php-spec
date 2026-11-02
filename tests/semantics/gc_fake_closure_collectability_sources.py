#!/usr/bin/env python3
"""Native-first fake-Closure GC eligibility and real-Closure control."""
from pathlib import Path
import hashlib

import global_constant_sources as family


ROOT = family.ROOT
FILES = {
    'fake-closure-kinds': ROOT / 'tests/semantics/gc_fake_closure_collectability_source.php',
    'fake-closure-status': ROOT / 'tests/semantics/gc_fake_closure_collectability_status.php',
    'fake-closure-clone-status': ROOT / 'tests/semantics/gc_fake_closure_clone_status.php',
    'fake-closure-reached': ROOT / 'tests/semantics/gc_fake_closure_reached_source.php',
    'fake-closure-producers-status': ROOT / 'tests/semantics/gc_fake_closure_producers_status.php',
    'fake-closure-fiber-enum-status': ROOT / 'tests/semantics/gc_fake_closure_fiber_enum_status.php',
    'fake-closure-named-reached': ROOT / 'tests/semantics/gc_fake_closure_named_reached.php',
    'fake-closure-method-reached': ROOT / 'tests/semantics/gc_fake_closure_method_reached.php',
    'fake-closure-fiber-reached': ROOT / 'tests/semantics/gc_fake_closure_fiber_reached.php',
}
family.CASES = {name: path.read_bytes() for name, path in FILES.items()}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {'fake-closure-kinds': 120, 'fake-closure-named-reached': 180,
                         'fake-closure-method-reached': 180, 'fake-closure-fiber-reached': 180}
EXPECTED_SHA256 = {
    'fake-closure-kinds': '78e5638dae892f4d9f5742bb3d9996351167ef1f55a4a128a93746e33906efe5',
    'fake-closure-status': '2625cb1e52a3f83480e1af875fe7261511a69687a20d401f5a77a010bffe0eea',
    'fake-closure-clone-status': 'd5a057d1ae5c51218ffd0f4c78e43cf4053d1e45bdc4d0decfdd2f14fea7aa5f',
    'fake-closure-reached': 'f9c9ed1710e2afd5a4785eafdd2699edc10ec3fe72b9007b4adc69c504690cde',
    'fake-closure-producers-status': '7b22195816c874189c2dc0127cf9b28f53ea4c53379ac962c3968865c0ad4749',
    'fake-closure-fiber-enum-status': 'ecaf71ac7d1c6c0e8595b69546d2f3bbe07fb6f7a4486debbba38e7cf3951bb9',
    'fake-closure-named-reached': '155b2890726478b34d7d1e7a667d05eb6d3a3aa6bd124816c7385cec914bdbed',
    'fake-closure-method-reached': 'a5740001f8c3de5f8ce4be0f32c99e8969153ef0ef1beb247a973bd1f67f15b1',
    'fake-closure-fiber-reached': 'e2c45c8021a32eba6709bc47f5f4c0e9108712b938050ef85626c769f91bcdbc',
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
