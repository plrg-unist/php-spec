<?php
class GC45Value { public $a = null; public $b = null; public $c = null; }
class GC45Leaf {}
class GC45X {
    public function __destruct() {
        global $mapWatch, $valueWatch, $firstKeyWatch, $secondKeyWatch, $yWatch, $leafWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($firstKeyWatch->get() === null), '|',
             (int) ($secondKeyWatch->get() !== null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|';
    }
}
class GC45Y {
    public function __destruct() {
        global $mapWatch, $valueWatch, $firstKeyWatch, $secondKeyWatch, $xWatch, $leafWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($firstKeyWatch->get() === null), '|',
             (int) ($secondKeyWatch->get() !== null), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($leafWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$tailKey = new stdClass;
$value = new GC45Value;
$x = new GC45X;
$y = new GC45Y;
$leaf = new GC45Leaf;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$firstKeyWatch = WeakReference::create($firstKey);
$map[$firstKey] = $value;
$map[$secondKey] = $value;
$map[$tailKey] = $leaf;
$secondKeyWatch = WeakReference::create($secondKey);
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$leafWatch = WeakReference::create($leaf);
unset($value, $x, $y, $leaf);
echo 'B|';
unset($firstKey);
echo 'P|', (int) ($firstKeyWatch->get() === null), '|',
     (int) ($valueWatch->get() !== null), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|',
     (int) ($leafWatch->get() !== null), '|';
unset($secondKey);
echo 'Q|', (int) ($secondKeyWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($leafWatch->get() !== null), '|';
unset($tailKey);
echo 'A|', (int) ($leafWatch->get() === null), '|',
     (int) ($mapWatch->get() !== null), '|';
unset($map);
echo 'Z|', (int) ($mapWatch->get() === null), '|';
