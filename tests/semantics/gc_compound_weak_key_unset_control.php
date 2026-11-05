<?php
class GcCompoundWeakUnsetValue33 { public function __destruct() { echo 'VALUE|'; } }
echo 'B|';
$target = new stdClass;
$key = WeakReference::create($target);
$map = new WeakMap;
$map[$key] = new GcCompoundWeakUnsetValue33;
unset($key);
echo 'AFTER|';
