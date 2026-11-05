<?php
class GC36WideValue {}
class GC36WideChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$key = new stdClass;
$key->first = new GC36WideChild;
$key->second = 1;
echo 'B|';
$map[$key] = new GC36WideValue;
echo 'A|';
