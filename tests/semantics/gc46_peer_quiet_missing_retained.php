<?php
class GC46PeerQuietValue { public $a = null; public $b = null; public $c = null; }
class GC46PeerQuietLeaf {}
class GC46PeerQuietX {
    public function __destruct() {
        global $mapWatch, $valueWatch, $keyWatch, $yWatch, $leafWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($keyWatch->get() === null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|';
    }
}
class GC46PeerQuietY {
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
$missingKey = new stdClass;
$value = new GC46PeerQuietValue;
$x = new GC46PeerQuietX;
$y = new GC46PeerQuietY;
$leaf = new GC46PeerQuietLeaf;
$value->c = $x;
$value->b = $y;
$value->a = $x;
$map[$key] = $value;
$map[$laterKey] = $leaf;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$keyWatch = WeakReference::create($key);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$leafWatch = WeakReference::create($leaf);
unset($value, $x, $y, $leaf);
echo 'B|', (int) isset($map[$missingKey]), '|',
     (int) empty($map[$missingKey]), '|';
$fallback = $map[$missingKey] ?? 'missing';
echo 'N|', $fallback, '|';
try {
    $discarded = $map[$missingKey];
    echo 'UNREACHED|';
} catch (Error $error) {
    echo 'E|', $error->getMessage(), '|', (int) isset($discarded), '|';
}
unset($error);
$held = $map[$key] ?? null;
echo 'R|', (int) ($held === $valueWatch->get()), '|';
unset($key);
echo 'K|', (int) ($keyWatch->get() === null), '|',
     (int) ($valueWatch->get() !== null), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|',
     (int) ($leafWatch->get() !== null), '|';
unset($held);
echo 'V|', (int) ($valueWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($leafWatch->get() !== null), '|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|';
