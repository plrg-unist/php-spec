#!/usr/bin/env python3
"""Independent native-first ordinary-caller materialized GC witnesses."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'nested-caller-local-protects-sibling': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcSavedRoot07 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcSavedProxy07 {}
function collect_saved_inner07($heldWeak) {
    $drop = new GcSavedRoot07;
    $drop->name = 'D';
    $proxy = new GcSavedProxy07;
    $proxy->back = $drop;
    $table = (array) $proxy;
    $drop->head = $table;
    $drop->tail = $proxy;
    $drop->extra = 8;
    $dropWeak = WeakReference::create($drop);
    unset($proxy, $table, $drop);
    echo 'I|', gc_collect_cycles(), '|';
    echo $heldWeak->get() !== null && $dropWeak->get() === null ? 'protected|' : 'BAD|';
    echo gc_collect_cycles(), '|';
}
function collect_saved_relay07($heldWeak) {
    collect_saved_inner07($heldWeak);
    echo 'R|';
}
function collect_saved_outer07() {
    $held = new GcSavedRoot07;
    $held->name = 'H';
    $proxy = new GcSavedProxy07;
    $proxy->back = $held;
    $table = (array) $proxy;
    $held->head = $table;
    $held->tail = $proxy;
    $held->extra = 7;
    $heldWeak = WeakReference::create($held);
    unset($proxy, $table);
    collect_saved_relay07($heldWeak);
    echo $heldWeak->get() !== null ? 'returned|' : 'BAD|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $heldWeak->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|END';
}
collect_saved_outer07();
''',
    'function-caller-mutation-resurrection': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcResurrectRoot07 {
    public $head;
    public $tail;
    public function __destruct() {
        global $saved07;
        echo 'D|';
        $old = $this->head;
        $this->head = $this->tail;
        $this->tail = $old;
        $saved07 = $this;
    }
}
#[AllowDynamicProperties]
class GcResurrectProxy07 {}
function collect_resurrect_frame07() {
    global $saved07;
    $root = new GcResurrectRoot07;
    $proxy = new GcResurrectProxy07;
    $proxy->back = $root;
    $table = (array) $proxy;
    $root->head = $table;
    $root->tail = $proxy;
    $root->extra = 7;
    $weakRoot = WeakReference::create($root);
    $weakProxy = WeakReference::create($proxy);
    unset($proxy, $table, $root);
    echo 'P|', gc_collect_cycles(), '|';
    echo $weakRoot->get() !== null && $weakProxy->get() !== null ? 'saved|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($saved07);
    echo gc_collect_cycles(), '|';
    echo $weakRoot->get() === null && $weakProxy->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|END';
}
collect_resurrect_frame07();
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('cached ordinary property-table collection', b'I|')
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
EXPECTED_SHA256 = {
    'nested-caller-local-protects-sibling': 'f699e754fe4b76216e0eab1397e455988af2837e120f3b40f5bca8f044712140',
    'function-caller-mutation-resurrection': '23e44cdf10b1835d5ca66517f6f7e5c93adeece43ada6497ad49cc0591520afd',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
