<?php
class GC38IncomingValue { public $child = null; }
class GC38IncomingChild { public function __destruct() { echo 'C|'; } }
$inner = new WeakMap;
$outer = new WeakMap;
$outer[$inner] = new stdClass;
$key = new stdClass;
$value = new GC38IncomingValue;
$value->child = new GC38IncomingChild;
$inner[$key] = $value;
unset($value);
echo 'B|';
unset($inner);
echo 'A|';
