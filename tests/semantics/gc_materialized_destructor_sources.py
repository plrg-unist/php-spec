#!/usr/bin/env python3
"""Native-first materialized ordinary cycles with collector destructors."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'materialized-shared-table-dtor': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcDtorRoot05 {
    public $head;
    public $tail;
    function __destruct() { echo 'D|'; }
}
#[AllowDynamicProperties]
class GcDtorProxy05 {}
$root = new GcDtorRoot05;
$proxy = new GcDtorProxy05;
$proxy->back = $root;
$table = (array) $proxy;
$root->head = $table;
$root->tail = $proxy;
$root->extra = 7;
$wr = WeakReference::create($root);
$wp = WeakReference::create($proxy);
unset($table, $root, $proxy);
echo 'P|', gc_collect_cycles(), '|';
echo $wr->get() === null && $wp->get() === null ? 'dead|' : 'BAD|';
echo gc_collect_cycles(), '|END';
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('cached ordinary property-table collection', b'P|')
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
EXPECTED_SHA256 = {
    'materialized-shared-table-dtor': '48eb73995b462093f734026cd4a2e24f6ca3f67a6e8de96658ccd906c7160a2e',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
