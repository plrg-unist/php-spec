<?php
class GC38RetainedValue { public $child = null; }
class GC38RetainedChild { public function __destruct() { echo 'C|'; } }
$map = new WeakMap;
$key = new stdClass;
$value = new GC38RetainedValue;
$map[$key] = $value;
$child = new GC38RetainedChild;
$value->child = $child;
unset($value);
echo 'B|';
unset($map);
echo 'A|';
unset($child);
echo 'X|';
