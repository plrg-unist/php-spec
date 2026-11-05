<?php
class GC46Value { public $a = null; public $b = null; public $c = null; }
class GC46Leaf {}
class GC46X {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $yWatch, $leafWatch;
        echo 'X|', (int) ($mapWatch->get() === null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() === null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($leafWatch->get() === null), '|';
    }
}
class GC46Y {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $xWatch, $leafWatch, $failure;
        echo 'Y|', (int) ($mapWatch->get() === null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() === null), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($leafWatch->get() === null), '|';
        throw $failure;
    }
}
$failure = new Exception('fetched-46');
$map = new WeakMap;
$key = new stdClass;
$otherKey = new stdClass;
$value = new GC46Value;
$x = new GC46X;
$y = new GC46Y;
$leaf = new GC46Leaf;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$keyWatch = WeakReference::create($key);
$map[$key] = $value;
$map[$otherKey] = $leaf;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$leafWatch = WeakReference::create($leaf);
unset($value, $x, $y, $leaf);
echo 'B|', (int) isset($map[$key]), '|', (int) empty($map[$key]), '|';
$fetched = $map[$key];
echo 'F|', (int) ($valueWatch->get() === $fetched), '|';
unset($key);
echo 'K|', (int) ($keyWatch->get() === null), '|',
     (int) ($valueWatch->get() !== null), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|',
     (int) ($leafWatch->get() !== null), '|';
unset($map);
echo 'M|', (int) ($mapWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|',
     (int) ($valueWatch->get() !== null), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|';
try {
    unset($fetched);
} catch (Exception $e) {
    echo 'T|', (int) ($e === $failure), '|', $e->getMessage(), '|';
}
echo 'A|', (int) ($valueWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|';
