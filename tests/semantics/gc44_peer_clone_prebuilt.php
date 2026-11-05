<?php
class GC44PeerCloneValue { public $a = null; public $b = null; public $c = null; }
class GC44PeerCloneX {
    public function __destruct() {
        global $mapWatch, $seedWatch, $keyWatch, $yWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($seedWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($yWatch->get() !== null), '|';
    }
}
class GC44PeerCloneY {
    public function __destruct() {
        global $mapWatch, $seedWatch, $keyWatch, $xWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($seedWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($xWatch->get() === null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$seed = new GC44PeerCloneValue;
$x = new GC44PeerCloneX;
$y = new GC44PeerCloneY;
$seed->a = $x;
$seed->b = $x;
$seed->c = $y;
$mapWatch = WeakReference::create($map);
$seedWatch = WeakReference::create($seed);
$keyWatch = WeakReference::create($key);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
unset($x, $y);
echo 'B|';
$map[$key] = clone $seed;
unset($seed);
echo 'S|', (int) ($seedWatch->get() === null), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($keyWatch->get() !== null), '|';
