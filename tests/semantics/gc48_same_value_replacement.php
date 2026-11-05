<?php
class GC48SameValue { public $child = null; }
class GC48SameChild { public function __destruct() { echo 'C|'; } }
$map = new WeakMap;
$key = new stdClass;
$value = new GC48SameValue;
$child = new GC48SameChild;
$value->child = $child;
unset($child);
$map[$key] = $value;
echo 'B|';
$map[$key] = $value;
echo 'A|';
unset($map, $value, $key);
