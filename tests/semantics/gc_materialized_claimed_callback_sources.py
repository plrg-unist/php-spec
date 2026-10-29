#!/usr/bin/env python3
"""Native-first shared-table count roles during ordinary GC callbacks."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'materialized-proxy-first-destructor': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcClaimDtorRoot06 {
    public $head;
    public $tail;
    public function __destruct() { echo 'D|'; }
}
#[AllowDynamicProperties]
class GcClaimDtorProxy06 {}
$root = new GcClaimDtorRoot06;
$proxy = new GcClaimDtorProxy06;
$proxy->back = $root;
$table = (array) $proxy;
$root->head = $proxy;
$root->tail = $table;
$root->extra = 7;
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
family.BASELINE = ('cached ordinary property-table collection', b'P|0|live|0|')
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
EXPECTED_SHA256 = {
    'materialized-proxy-first-destructor': '5019bdcfc809f178a1f5ccb9fe73be0d76121f52c4b52800afc32e1c16ff44fb',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
