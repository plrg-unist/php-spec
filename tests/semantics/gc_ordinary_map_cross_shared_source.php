<?php
class GcOrdinaryCrossLeaf34 {}
$outer = new WeakMap;
$other = new WeakMap;
$inner = new WeakMap;
$first = new stdClass;
$second = new stdClass;
$value = new GcOrdinaryCrossLeaf34;
$watch = WeakReference::create($value);
$inner[$first] = $value;
$inner[$second] = $value;
$other[$inner] = $value;
$outer[$inner] = $value;
unset($value);
echo 'B|', $watch->get() === null ? 'dead|' : 'live|';
unset($inner);
echo 'A|', $watch->get() === null ? 'dead|' : 'live|';
