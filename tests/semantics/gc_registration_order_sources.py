#!/usr/bin/env python3
"""Native-first callback-free WeakMap association-order collection cases."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'reverse-two-proxy': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcRegistrationBag03 {}
$left = new WeakMap;
$right = new WeakMap;
$key = new stdClass;
$proxy = new GcRegistrationBag03;
$other = new GcRegistrationBag03;
$right[$key] = $proxy;
$left[$key] = $other;
$proxy->back = $key;
$table = (array) $proxy;
$other->table = $table;
$key->self = $key;
$wk = WeakReference::create($key);
$wp = WeakReference::create($proxy);
$wo = WeakReference::create($other);
unset($key, $proxy, $other, $table);
echo 'B|', gc_collect_cycles(), '|';
echo $wk->get() === null && $wp->get() === null && $wo->get() === null ? 'dead|' : 'BAD|';
echo gc_collect_cycles(), '|';
unset($left, $right);
echo gc_collect_cycles(), '|END';
''',
    'interleaved-two-keys': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcRegistrationLeaf03 { public $back; }
$mapA = new WeakMap;
$mapB = new WeakMap;
$mapC = new WeakMap;
$one = new stdClass;
$two = new stdClass;
$a = new GcRegistrationLeaf03;
$b = new GcRegistrationLeaf03;
$c = new GcRegistrationLeaf03;
$d = new GcRegistrationLeaf03;
$e = new GcRegistrationLeaf03;
$f = new GcRegistrationLeaf03;
$mapC[$one] = $a;
$mapB[$two] = $b;
$mapA[$one] = $c;
$mapC[$two] = $d;
$mapB[$one] = $e;
$mapA[$two] = $f;
$a->back = $one; $c->back = $one; $e->back = $one;
$b->back = $two; $d->back = $two; $f->back = $two;
$one->self = $one; $two->self = $two;
$wone = WeakReference::create($one);
$wtwo = WeakReference::create($two);
$wa = WeakReference::create($a);
$wb = WeakReference::create($b);
$held = $one;
unset($one, $two, $a, $b, $c, $d, $e, $f);
echo 'B|', gc_collect_cycles(), '|';
echo $wone->get() !== null && $wa->get() !== null && $wtwo->get() === null && $wb->get() === null ? 'split|' : 'BAD|';
unset($held);
echo gc_collect_cycles(), '|';
echo $wone->get() === null && $wa->get() === null ? 'dead|' : 'BAD|';
unset($mapA, $mapB, $mapC);
echo gc_collect_cycles(), '|END';
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('WeakMap dimension protocol outside first insertion', b'')
family.MODEL_TIMEOUTS = {name: 300 for name in family.CASES}
EXPECTED_SHA256 = {
    'reverse-two-proxy': '1ef2b37ed9c40cd4f6f26f6d4cad44059add8e3525732f1ce1fbcb228fb45205',
    'interleaved-two-keys': 'b5cd1bc0327bd022edefcc8605e5edfc8a097764d8567e660ccc266a8422816f',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
