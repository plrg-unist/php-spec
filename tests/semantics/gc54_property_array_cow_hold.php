<?php
class GC54Value { public $items = null; }
class GC54X {
    public function __destruct() {
        global $map, $scalarKey, $keyWatch, $valueWatch, $yWatch;
        echo 'X|', (int) ($keyWatch->get() === null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($map[$scalarKey] === 0), '|';
    }
}
class GC54Y {
    public function __destruct() {
        global $map, $scalarKey, $keyWatch, $valueWatch, $xWatch;
        echo 'Y|', (int) ($keyWatch->get() === null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($map[$scalarKey] === 0), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$scalarKey = new stdClass;
$keyWatch = WeakReference::create($key);
$value = new GC54Value;
$x = new GC54X;
$y = new GC54Y;
$array = [$x, $y, $x, 0];
$value->items = $array;
$valueWatch = WeakReference::create($value);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
unset($array, $x, $y);
echo 'B|';
$map[$key] = $value;
$map[$scalarKey] = 0;
$held = $value->items;
$copy = $held;
unset($copy[0], $value);
echo 'R|', (int) ($held[0] === $held[2]), '|',
     (int) ($copy[1] === $held[1]), '|',
     (int) ($copy[2] === $held[2]), '|';
unset($key);
echo 'H|', (int) ($keyWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($held[0] === $copy[2]), '|';
unset($held);
echo 'D|', (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|';
unset($copy);
echo 'V|', (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($map[$scalarKey] === 0), '|';
unset($map);
echo 'A|';
