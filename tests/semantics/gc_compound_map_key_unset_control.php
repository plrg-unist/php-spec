<?php
class GcCompoundMapUnsetValue33 { public function __destruct() { echo 'VALUE|'; } }
echo 'B|';
$outer = new WeakMap;
$inner = new WeakMap;
$outer[$inner] = new GcCompoundMapUnsetValue33;
unset($inner);
echo 'AFTER|';
