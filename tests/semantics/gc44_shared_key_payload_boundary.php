<?php
class GC44SharedValue { public $a = null; public $b = null; }
class GC44SharedLeaf {}
class GC44SharedChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$other = new WeakMap;
$privateKey = new stdClass;
$sharedKey = new stdClass;
$map[$privateKey] = new GC44SharedLeaf;
$other[$sharedKey] = new GC44SharedLeaf;
$value = new GC44SharedValue;
$value->a = new GC44SharedChild;
echo 'B|';
$map[$sharedKey] = $value;
echo 'A|';
