<?php
class GcCompoundMapLeaf33 {}
class GcCompoundMapNonemptyUnset33 { public function __destruct() { echo 'VALUE|'; } }
echo 'B|';
$plain = new stdClass;
$key = new WeakMap;
$key[$plain] = new GcCompoundMapLeaf33;
$map = new WeakMap;
$map[$key] = new GcCompoundMapNonemptyUnset33;
unset($key);
echo 'AFTER|';
