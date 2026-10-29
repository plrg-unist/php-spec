#!/usr/bin/env python3
"""Native-first materialized cycles collected from an ordinary caller frame."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'function-local-protects-sibling': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcFrameRoot07 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcFrameProxy07 {}
function collect_in_frame07() {
    $held = new GcFrameRoot07;
    $held->name = 'H';
    $heldProxy = new GcFrameProxy07;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcFrameRoot07;
    $drop->name = 'D';
    $dropProxy = new GcFrameProxy07;
    $dropProxy->back = $drop;
    $dropTable = (array) $dropProxy;
    $drop->head = $dropTable;
    $drop->tail = $dropProxy;
    $drop->extra = 8;
    $wd = WeakReference::create($drop);
    unset($dropProxy, $dropTable);

    echo 'P|', gc_collect_cycles(), '|';
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|END';
}
collect_in_frame07();
''',
    'method-receiver-protects-sibling': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcMethodRoot07 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcMethodProxy07 {}
class GcMethodOwner07 {
    public $kept;
    public function collect() {
        $held = new GcMethodRoot07;
        $held->name = 'H';
        $heldProxy = new GcMethodProxy07;
        $heldProxy->back = $held;
        $heldTable = (array) $heldProxy;
        $held->head = $heldTable;
        $held->tail = $heldProxy;
        $held->extra = 7;
        $wh = WeakReference::create($held);
        $this->kept = $held;
        unset($held, $heldProxy, $heldTable);

        $drop = new GcMethodRoot07;
        $drop->name = 'D';
        $dropProxy = new GcMethodProxy07;
        $dropProxy->back = $drop;
        $dropTable = (array) $dropProxy;
        $drop->head = $dropTable;
        $drop->tail = $dropProxy;
        $drop->extra = 8;
        $wd = WeakReference::create($drop);
        unset($dropProxy, $dropTable);

        echo 'P|', gc_collect_cycles(), '|';
        unset($drop);
        echo gc_collect_cycles(), '|';
        echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
        echo gc_collect_cycles(), '|';
        $this->kept = null;
        echo gc_collect_cycles(), '|';
        echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
        echo gc_collect_cycles(), '|END';
    }
}
(new GcMethodOwner07)->collect();
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('cached ordinary property-table collection', b'P|0|')
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
EXPECTED_SHA256 = {
    'function-local-protects-sibling': 'e3b63662a7f979589535f46f3f619f15d06732570fcac69e1df2651fe97bc826',
    'method-receiver-protects-sibling': '275f23f83a356c55b47f83eafafc7f282998b2e3587a0231439185ede2e73dad',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
