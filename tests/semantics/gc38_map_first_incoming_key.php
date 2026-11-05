<?php
class GC38IncomingValue { public $child = null; }
class GC38IncomingChild { public function __destruct() { echo 'C|'; } }
class GC38IncomingOuterValue {}
$inner = new WeakMap;
$outer = new WeakMap;
$outer[$inner] = new GC38IncomingOuterValue;
$key = new stdClass;
$value = new GC38IncomingValue;
$value->child = new GC38IncomingChild;
$inner[$key] = $value;
unset($value);
echo 'B|';
unset($inner);
echo 'A|';
