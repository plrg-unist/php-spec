<?php
class GC39Owner3Value {
    public $child = null;
}
class GC39Owner3Child {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC39Owner3Value;
$map[$key] = $value;
$child = new GC39Owner3Child;
$extra = $child;
$value->child = $child;
unset($value);
echo 'B|';
unset($map);
echo 'A|';
unset($child);
echo 'X|';
unset($extra);
echo 'Y|';
