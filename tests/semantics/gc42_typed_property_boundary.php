<?php
class GC42TypedValue {
    public GC42TypedChild $child;
    public $other = null;
}
class GC42TypedLeaf {}
class GC42TypedChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$valueKey = new stdClass;
$leafKey = new stdClass;
$value = new GC42TypedValue;
$leaf = new GC42TypedLeaf;
$map[$valueKey] = $value;
$map[$leafKey] = $leaf;
$value->child = new GC42TypedChild;
unset($value, $leaf);
echo 'B|';
unset($map);
echo 'A|';
