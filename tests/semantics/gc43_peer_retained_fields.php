<?php
class GC43PeerRetainedValue { public $a = null; public $b = null; public $c = null; }
class GC43PeerRetainedX {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $yWatch;
        echo 'X|', (int) ($mapWatch->get() === null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($yWatch->get() !== null), '|';
    }
}
class GC43PeerRetainedY {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $xWatch;
        echo 'Y|', (int) ($mapWatch->get() === null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($xWatch->get() === null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC43PeerRetainedValue;
$map[$key] = $value;
$x = new GC43PeerRetainedX;
$y = new GC43PeerRetainedY;
$value->c = $y;
$value->b = $x;
$value->a = $x;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$keyWatch = WeakReference::create($key);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
unset($x, $y);
echo 'B|';
unset($map);
echo 'M|', (int) ($mapWatch->get() === null), '|',
     (int) ($valueWatch->get() !== null), '|',
     (int) ($keyWatch->get() !== null), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|';
unset($value);
echo 'A|', (int) ($valueWatch->get() === null), '|',
     (int) ($keyWatch->get() !== null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|';
