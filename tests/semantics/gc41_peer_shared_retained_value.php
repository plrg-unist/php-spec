<?php
class GC41PeerSharedValue { public $child = null; }
class GC41PeerSharedLeaf {}
class GC41PeerSharedChild {
    public function __destruct() {
        global $mapWatch, $aWatch, $bWatch, $leafWatch;
        echo 'C|', (int) ($mapWatch->get() === null), '|',
             (int) ($aWatch->get() === null), '|',
             (int) ($bWatch->get() === null), '|',
             (int) ($leafWatch->get() === null), '|';
    }
}
$map = new WeakMap;
$k0 = new stdClass;
$k1 = new stdClass;
$k2 = new stdClass;
$k3 = new stdClass;
$a = new GC41PeerSharedValue;
$b = new GC41PeerSharedValue;
$leaf = new GC41PeerSharedLeaf;
$child = new GC41PeerSharedChild;
$map[$k0] = $a;
$map[$k1] = $leaf;
$map[$k2] = $b;
$map[$k3] = $a;
$a->child = $child;
$b->child = $child;
$mapWatch = WeakReference::create($map);
$aWatch = WeakReference::create($a);
$bWatch = WeakReference::create($b);
$leafWatch = WeakReference::create($leaf);
$childWatch = WeakReference::create($child);
unset($b, $leaf, $child);
echo 'B|';
unset($map);
echo 'M|', (int) ($mapWatch->get() === null), '|',
     (int) ($aWatch->get() !== null), '|',
     (int) ($bWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|',
     (int) ($childWatch->get() !== null), '|';
unset($a);
echo 'A|', (int) ($aWatch->get() === null), '|',
     (int) ($childWatch->get() === null), '|';
