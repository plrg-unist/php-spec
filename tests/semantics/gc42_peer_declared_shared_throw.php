<?php
class GC42PeerValue {
    public $a = null;
    public $b = null;
    public $c = null;
    public $d = null;
}
class GC42PeerLeaf {}
class GC42PeerX {
    public function __destruct() {
        global $mapWatch, $valueWatch, $leafWatch, $yWatch, $zWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($zWatch->get() !== null), '|';
    }
}
class GC42PeerY {
    public function __destruct() {
        global $mapWatch, $valueWatch, $leafWatch, $xWatch, $zWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($zWatch->get() !== null), '|';
        throw new Exception('declared-42');
    }
}
class GC42PeerZ {
    public function __destruct() {
        global $mapWatch, $valueWatch, $leafWatch, $xWatch, $yWatch;
        echo 'Z|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|',
             (int) ($xWatch->get() === null), '|',
             (int) ($yWatch->get() === null), '|';
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$value = new GC42PeerValue;
$leaf = new GC42PeerLeaf;
$map[$firstKey] = $value;
$map[$secondKey] = $leaf;
$x = new GC42PeerX;
$y = new GC42PeerY;
$z = new GC42PeerZ;
$value->d = $z;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$leafWatch = WeakReference::create($leaf);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$zWatch = WeakReference::create($z);
unset($x, $y, $z, $value, $leaf);
echo 'B|';
try { unset($map); echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($zWatch->get() === null), '|';
