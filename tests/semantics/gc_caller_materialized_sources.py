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
}
family.UNSUPPORTED = {}
family.BASELINE = ('cached ordinary property-table collection', b'P|0|')
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
EXPECTED_SHA256 = {
    'function-local-protects-sibling': 'e3b63662a7f979589535f46f3f619f15d06732570fcac69e1df2651fe97bc826',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
