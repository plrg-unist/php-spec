<?php
class GC47PeerRetainedValue { public $a = null; public $b = null; public $c = null; }
class GC47PeerRetainedLeaf {}
class GC47PeerRetainedX {
    public function __destruct() {
        global $map, $key, $mapWatch, $valueWatch, $keyWatch, $yWatch, $firstLeafWatch, $secondLeafWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($firstLeafWatch->get() !== null), '|',
             (int) ($secondLeafWatch->get() !== null), '|',
             (int) !isset($map[$key]), '|';
    }
}
class GC47PeerRetainedY {
    public function __destruct() {
        global $map, $key, $mapWatch, $valueWatch, $keyWatch, $xWatch, $firstLeafWatch, $secondLeafWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($firstLeafWatch->get() !== null), '|',
             (int) ($secondLeafWatch->get() !== null), '|',
             (int) !isset($map[$key]), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$firstLeafKey = new stdClass;
$secondLeafKey = new stdClass;
$value = new GC47PeerRetainedValue;
$x = new GC47PeerRetainedX;
$y = new GC47PeerRetainedY;
$firstLeaf = new GC47PeerRetainedLeaf;
$secondLeaf = new GC47PeerRetainedLeaf;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$map[$key] = $value;
$map[$firstLeafKey] = $firstLeaf;
$map[$secondLeafKey] = $secondLeaf;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$keyWatch = WeakReference::create($key);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$firstLeafWatch = WeakReference::create($firstLeaf);
$secondLeafWatch = WeakReference::create($secondLeaf);
unset($value, $x, $y, $firstLeaf, $secondLeaf);
$fetched = $map[$key];
echo 'B|';
unset($map[$key]);
echo 'U|', (int) isset($map[$key]), '|', (int) empty($map[$key]), '|',
     (int) ($valueWatch->get() === $fetched), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|',
     (int) ($keyWatch->get() !== null), '|';
unset($fetched);
echo 'V|', (int) ($valueWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($keyWatch->get() !== null), '|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($firstLeafWatch->get() === null), '|',
     (int) ($secondLeafWatch->get() === null), '|',
     (int) ($keyWatch->get() !== null), '|';
