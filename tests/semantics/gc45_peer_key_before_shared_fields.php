<?php
class GC45PeerBeforeValue { public $a = null; public $b = null; public $c = null; }
class GC45PeerBeforeLeaf {}
class GC45PeerBeforeX {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $yWatch, $leafWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() === null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|';
    }
}
class GC45PeerBeforeY {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $xWatch, $leafWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() === null), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($leafWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$laterKey = new stdClass;
$value = new GC45PeerBeforeValue;
$x = new GC45PeerBeforeX;
$y = new GC45PeerBeforeY;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$keyWatch = WeakReference::create($key);
$map[$key] = $value;
$leaf = new GC45PeerBeforeLeaf;
$map[$laterKey] = $leaf;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$leafWatch = WeakReference::create($leaf);
unset($value, $x, $y, $leaf);
echo 'B|';
unset($key);
echo 'K|', (int) ($keyWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($leafWatch->get() !== null), '|',
     (int) ($mapWatch->get() !== null), '|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|';
