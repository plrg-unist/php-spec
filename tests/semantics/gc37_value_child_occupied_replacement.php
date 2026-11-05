<?php
class GC37OldValue {}
class GC37NewValue { public $child = null; }
class GC37ReplacementChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$key = new stdClass;
$map[$key] = new GC37OldValue;
$newValue = new GC37NewValue;
$newValue->child = new GC37ReplacementChild;
echo 'B|';
$map[$key] = $newValue;
echo 'A|';
