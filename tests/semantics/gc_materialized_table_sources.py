#!/usr/bin/env python3
"""Native-first physical GC for ordinary materialized property-table graphs."""
from pathlib import Path
import hashlib

import global_constant_sources as family


family.CASES = {
    'mixed-components': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class PhysicalGraph01 { public $left; public $right; public $rows; }
$alias = null;
$a = new PhysicalGraph01;
$b = new PhysicalGraph01;
$c = new stdClass;
$other = new PhysicalGraph01;
$a->left = $b;
$a->right = $b;
$b->left = $a;
$b->right = $a;
$alias = $c;
$a->rows = [&$alias];
$b->rows = $a->rows;
$a->extra = $c;
$b->extra = 7;
$c->owner = $a;
$other->left = $other;
$other->extra = $other;
$wa = WeakReference::create($a);
$wb = WeakReference::create($b);
$wc = WeakReference::create($c);
$wo = WeakReference::create($other);
unset($a, $b, $c, $other, $alias);
echo 'B|';
echo gc_collect_cycles(), '|';
echo $wa->get() === null ? 'A|' : 'BAD|', $wb->get() === null ? 'B|' : 'BAD|', $wc->get() === null ? 'C|' : 'BAD|', $wo->get() === null ? 'O|' : 'BAD|';
echo gc_collect_cycles(), '|';
''',
    'zero-declared-shared-cast': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class PhysicalDynamic01 {}
$outside = 7;
$node = new PhysicalDynamic01;
$node->self = $node;
$node->slot =& $outside;
$watch = WeakReference::create($node);
$view = (array) $node;
$copy = $view;
unset($outside);
$copy['slot'] = 8;
$split = $copy['slot'];
unset($copy, $node);
echo 'B|';
echo gc_collect_cycles(), '|', $view['slot'], '|', $split, '|', $watch->get() !== null ? 'L|' : 'BAD|';
unset($view);
echo gc_collect_cycles(), '|', $watch->get() === null ? 'D|' : 'BAD|', gc_collect_cycles(), '|';
''',
    'typed-cell-detachment': br'''<?php
gc_disable();
#[AllowDynamicProperties]
class PhysicalTyped01 { public int $guard = 7; public $edge; }
$node = new PhysicalTyped01;
$node->edge = $node;
$node->extra = $node;
$alias =& $node->guard;
$watch = WeakReference::create($node);
unset($node);
echo 'B|';
echo gc_collect_cycles(), '|', $watch->get() === null ? 'D|' : 'BAD|', $alias, '|';
$alias = 'free';
echo $alias, '|', gc_collect_cycles(), '|';
''',
}
family.UNSUPPORTED = {}
family.BASELINE = ('cached ordinary property-table collection', b'B|')
family.MODEL_TIMEOUTS = {name: 240 for name in family.CASES}
EXPECTED_SHA256 = {
    'mixed-components': '317e65fa83b37f74d7c07ea8f543cffebcc12a52b5f5054b78f9e3c444020dcd',
    'zero-declared-shared-cast': 'eaeedc81a59b7993cf27f296fb32bb76f5d8887f1920e6ab0364379a53c14075',
    'typed-cell-detachment': '2595feab1c3693cce34ae5ffc2dcc256b05d38bb6a1d4b9442e458968c5654dc',
}
assert {name: hashlib.sha256(source).hexdigest() for name, source in family.CASES.items()} == EXPECTED_SHA256

family_fingerprint = family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(family.ROOT)): family.sha(__file__)})


family.fingerprint = fingerprint


if __name__ == '__main__':
    family.main()
