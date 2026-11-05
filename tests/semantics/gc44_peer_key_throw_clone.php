<?php
class GC44PeerKeyValue { public $a = null; public $b = null; public $c = null; }
class GC44PeerKeyX {
    public function __destruct() {
        global $mapWatch, $seedWatch, $yWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($seedWatch->get() === null), '|',
             (int) ($yWatch->get() !== null), '|';
    }
}
class GC44PeerKeyY {
    public function __destruct() {
        global $mapWatch, $seedWatch, $xWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($seedWatch->get() === null), '|',
             (int) ($xWatch->get() === null), '|';
    }
}
function gc44PeerFailKey() {
    global $seed, $seedWatch, $xWatch, $yWatch;
    $seed = null;
    echo 'K|', (int) ($seedWatch->get() === null), '|',
         (int) ($xWatch->get() !== null), '|',
         (int) ($yWatch->get() !== null), '|';
    throw new Exception('key-44');
}
$map = new WeakMap;
$seed = new GC44PeerKeyValue;
$x = new GC44PeerKeyX;
$y = new GC44PeerKeyY;
$seed->a = $x;
$seed->b = $x;
$seed->c = $y;
$mapWatch = WeakReference::create($map);
$seedWatch = WeakReference::create($seed);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
unset($x, $y);
echo 'B|';
try { $map[gc44PeerFailKey()] = clone $seed; echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'A|', (int) ($mapWatch->get() !== null), '|',
     (int) ($seedWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|';
