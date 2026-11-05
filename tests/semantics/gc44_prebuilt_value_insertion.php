<?php
class GC44Value { public $a = null; public $b = null; public $c = null; }
class GC44Leaf {}
class GC44X {
    public function __destruct() {
        global $mapWatch, $valueWatch, $yWatch, $leafWatch, $firstKeyWatch, $secondKeyWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($yWatch->get() !== null), '|',
             (int) ($leafWatch->get() !== null), '|',
             (int) ($firstKeyWatch->get() !== null), '|',
             (int) ($secondKeyWatch->get() !== null), '|';
    }
}
class GC44Y {
    public function __destruct() {
        global $mapWatch, $valueWatch, $xWatch, $leafWatch, $firstKeyWatch, $secondKeyWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($xWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|',
             (int) ($firstKeyWatch->get() !== null), '|',
             (int) ($secondKeyWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$thirdKey = new stdClass;
$value = new GC44Value;
$x = new GC44X;
$y = new GC44Y;
$value->c = $y;
$value->b = $x;
$value->a = $x;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$firstKeyWatch = WeakReference::create($firstKey);
$secondKeyWatch = WeakReference::create($secondKey);
unset($x, $y);
echo 'B|';
$map[$firstKey] = $value;
echo '1|';
$map[$secondKey] = $value;
echo '2|';
$leaf = $map[$thirdKey] = new GC44Leaf;
$leafWatch = WeakReference::create($leaf);
echo '3|', (int) ($leafWatch->get() === $leaf), '|';
unset($leaf, $value);
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|',
     (int) ($firstKeyWatch->get() !== null), '|',
     (int) ($secondKeyWatch->get() !== null), '|';
