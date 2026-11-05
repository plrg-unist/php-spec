<?php
class GcCompoundMapLeaf33 {}
class GcCompoundMapNonemptyUnset33 { public function __destruct() { echo 'VALUE|'; } }
echo 'B|';
$plain = new stdClass;
$second = new stdClass;
$key = new WeakMap;
$leaf = new GcCompoundMapLeaf33;
$key[$plain] = $leaf;
$key[$second] = $leaf;
$map = new WeakMap;
$map[$key] = new GcCompoundMapNonemptyUnset33;
unset($key);
echo 'AFTER|';
