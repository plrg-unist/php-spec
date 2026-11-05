<?php
class GC40TwoFieldsValue { public $child = null; }
class GC40TwoFieldsChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$first = new GC40TwoFieldsValue;
$second = new GC40TwoFieldsValue;
$map[$firstKey] = $first;
$map[$secondKey] = $second;
$first->child = new GC40TwoFieldsChild;
$second->child = new GC40TwoFieldsChild;
unset($first, $second);
echo 'B|';
unset($map);
echo 'A|';
