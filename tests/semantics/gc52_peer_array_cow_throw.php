<?php
class GC52PeerValue { public $child = null; }
function makeCowFailure52() { return new Exception('array-52'); }
class GC52PeerX {
    public function __destruct() {
        global $aWatch, $bWatch, $mapWatch, $keyWatch;
        echo 'X|', (int) ($aWatch->get() === null), '|',
             (int) ($bWatch->get() === null), '|',
             (int) ($mapWatch->get() !== null), '|',
             (int) ($keyWatch->get() !== null), '|';
    }
}
class GC52PeerY {
    public function __destruct() {
        global $aWatch, $bWatch, $mapWatch, $keyWatch, $failure;
        echo 'Y|', (int) ($bWatch->get() === null), '|',
             (int) ($aWatch->get() !== null), '|',
             (int) ($mapWatch->get() !== null), '|',
             (int) ($keyWatch->get() !== null), '|';
        throw $failure;
    }
}
$failure = makeCowFailure52();
$map = new WeakMap;
$key = new stdClass;
$a = new GC52PeerValue;
$a->child = new GC52PeerX;
$b = new GC52PeerValue;
$b->child = new GC52PeerY;
$mapWatch = WeakReference::create($map);
$keyWatch = WeakReference::create($key);
$aWatch = WeakReference::create($a);
$bWatch = WeakReference::create($b);
echo 'B|';
$map[$key] = [$a, $b, $a];
unset($a, $b);
$copy = $map[$key];
unset($copy[0]);
echo 'S|', (int) !isset($copy[0]), '|',
     (int) ($copy[1] === $bWatch->get()), '|',
     (int) ($copy[2] === $aWatch->get()), '|';
unset($copy);
echo 'D|', (int) ($aWatch->get() !== null), '|',
     (int) ($bWatch->get() !== null), '|';
$after = 0;
try {
    unset($map);
    $after = 1;
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo 'T|', (int) ($e === $failure), '|', $trace[0]['function'], '|',
         $after, '|', (int) ($mapWatch->get() === null), '|',
         (int) ($aWatch->get() === null), '|',
         (int) ($bWatch->get() === null), '|',
         (int) ($keyWatch->get() !== null), '|';
}
echo 'A|';
