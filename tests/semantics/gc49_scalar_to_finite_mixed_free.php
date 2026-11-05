<?php
class GC49Value { public $child = null; }
class GC49Child { public function __destruct() { echo 'C|'; } }
$map = new WeakMap;
$key = new stdClass;
$otherKey = new stdClass;
$map[$key] = 'seed-49';
$incoming = new GC49Value;
$child = new GC49Child;
$incoming->child = $child;
$outside = $incoming;
echo 'B|';
$written = $map[$key] = $incoming;
echo 'R|', (int) ($written === $outside), '|',
     (int) ($map[$key] === $written), '|';
$map[$otherKey] = false;
echo 'Q|', (int) isset($map[$otherKey]), '|',
     (int) empty($map[$otherKey]), '|',
     (int) (($map[$otherKey] ?? 'missing') === false), '|';
unset($child, $incoming, $outside, $written);
echo 'H|';
unset($map);
echo 'A|';
