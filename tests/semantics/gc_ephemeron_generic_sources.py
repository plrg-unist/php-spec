#!/usr/bin/env python3
"""Native-first repeated ordinary and finite callback-free ephemeron GC."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'repeated-materialized-history': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcRepeated02 { public $next; public $again; }
$a = new GcRepeated02;
$b = new GcRepeated02;
$a->next = $b; $a->again = $b;
$b->next = $a; $b->again = $a;
$a->extra = 7; $b->extra = 8;
$wa = WeakReference::create($a);
$held = $a;
unset($a, $b);
echo 'B|', gc_collect_cycles(), '|', $wa->get() !== null ? 'live|' : 'BAD|';
unset($held);
echo gc_collect_cycles(), '|', $wa->get() === null ? 'dead|' : 'BAD|';
$c = new GcRepeated02;
$c->next = $c; $c->again = $c;
$c->extra = 9;
$wc = WeakReference::create($c);
unset($c);
echo gc_collect_cycles(), '|', $wc->get() === null ? 'fresh-dead|' : 'BAD|', gc_collect_cycles(), '|END';
''',
    'branching-entry-fixpoint': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcEphemeronValue02 { public $left; public $right; }
$map = new WeakMap;
$a = new stdClass; $b = new stdClass; $c = new stdClass;
$x = new GcEphemeronValue02; $y = new GcEphemeronValue02; $z = new GcEphemeronValue02;
$map[$a] = $x; $map[$b] = $y; $map[$c] = $z;
$x->left = $b; $x->right = [$b, $c];
$y->left = $c; $z->left = $a;
$x->extra = 11;
$wa = WeakReference::create($a); $wb = WeakReference::create($b); $wc = WeakReference::create($c);
$wx = WeakReference::create($x); $wy = WeakReference::create($y); $wz = WeakReference::create($z);
unset($b, $c, $x, $y, $z);
echo 'B|', gc_collect_cycles(), '|';
echo $wa->get() !== null && $wb->get() !== null && $wc->get() !== null && $wx->get() !== null && $wy->get() !== null && $wz->get() !== null ? 'protected|' : 'BAD|';
unset($a);
echo gc_collect_cycles(), '|';
echo $wa->get() === null && $wb->get() === null && $wc->get() === null && $wx->get() === null && $wy->get() === null && $wz->get() === null ? 'dead|' : 'BAD|';
echo gc_collect_cycles(), '|END';
''',
    'unheld-map-live-key': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcEphemeronLoop02 { public $left; public $right; }
$map = new WeakMap;
$key = new stdClass;
$value = new GcEphemeronLoop02;
$map[$key] = $value;
$value->left = [$map]; $value->right = $map;
$value->extra = 7;
$wm = WeakReference::create($map); $wv = WeakReference::create($value); $wk = WeakReference::create($key);
unset($map, $value);
echo 'B|', gc_collect_cycles(), '|';
echo $wm->get() === null && $wv->get() === null && $wk->get() !== null ? 'map-dead-key-live|' : 'BAD|';
unset($key);
echo gc_collect_cycles(), '|', $wk->get() === null ? 'key-dead|' : 'BAD|', gc_collect_cycles(), '|END';
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('WeakMap ephemeron collection', b'B|')
family.MODEL_TIMEOUTS = {name: 300 for name in family.CASES}
EXPECTED_SHA256 = {
    'repeated-materialized-history': '8c70139bfcac4679e41adc3ce8462fd93488d9f6387350a778d9d010dc7517a6',
    'branching-entry-fixpoint': '14fbc93f1bbaaf62f25de3bfd5cee21c7e764cf89c6dfd49a223b213a7a5d4b8',
    'unheld-map-live-key': '0ee8d1d3a2008597aa6f4c06321a0f0bd8691e8e01144f9b7c99c8a6d514c810',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
