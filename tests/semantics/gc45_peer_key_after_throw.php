<?php
class GC45PeerAfterValue { public $a = null; public $b = null; public $c = null; }
class GC45PeerAfterLeaf {}
class GC45PeerAfterX {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $yWatch, $leafWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|';
    }
}
class GC45PeerAfterY {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $xWatch, $leafWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($leafWatch->get() !== null), '|';
        throw new Exception('key-child-45');
    }
}
$map = new WeakMap;
$key = new stdClass;
$laterKey = new stdClass;
$value = new GC45PeerAfterValue;
$x = new GC45PeerAfterX;
$y = new GC45PeerAfterY;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$map[$key] = $value;
$keyWatch = WeakReference::create($key);
$leaf = new GC45PeerAfterLeaf;
$map[$laterKey] = $leaf;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$leafWatch = WeakReference::create($leaf);
unset($value, $x, $y, $leaf);
echo 'B|';
try {
    unset($key);
    echo 'UNREACHED|';
} catch (Exception $error) {
    echo 'T|', $error->getMessage(), '|';
}
echo 'K|', (int) ($keyWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($leafWatch->get() !== null), '|',
     (int) ($mapWatch->get() !== null), '|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|';
