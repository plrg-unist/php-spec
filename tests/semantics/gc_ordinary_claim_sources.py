#!/usr/bin/env python3
"""Native-first ordinary GC sibling claim order with a shared property table."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'inline-sibling-shared-table': br'''<?php
gc_disable();
class GcClaimRoot04 { public $head; public $tail; }
#[AllowDynamicProperties]
class GcClaimProxy04 {}
class GcClaimHeld04 { public function __destruct() {} }
$held = new GcClaimHeld04;
$root = new GcClaimRoot04;
$proxy = new GcClaimProxy04;
$proxy->back = $root;
$table = (array) $proxy;
$root->head = $proxy;
$root->tail = $table;
$wr = WeakReference::create($root);
$wp = WeakReference::create($proxy);
unset($proxy);
echo 'P|', gc_collect_cycles(), '|';
echo $wr->get() !== null && $wp->get() !== null ? 'live|' : 'BAD|';
unset($table);
echo gc_collect_cycles(), '|';
unset($root);
echo gc_collect_cycles(), '|';
echo $wr->get() === null && $wp->get() === null ? 'dead|' : 'BAD|';
echo gc_collect_cycles(), '|END';
''',
}
family.UNSUPPORTED = {}
family.MODEL_TIMEOUTS = {name: 180 for name in family.CASES}
EXPECTED_SHA256 = {
    'inline-sibling-shared-table': '2a104ea052891bf3144afe89b3575844bd57d77b9f617fd33f24fd99d48b9aad',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
