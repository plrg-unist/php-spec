<?php
class GC41PeerManyValue { public $child = null; }
class GC41PeerManyLeaf {}
class GC41PeerManyChild {
    public function __destruct() {
        global $visits, $mapWatch, $aWatch, $bWatch, $cWatch, $leafWatch;
        ++$visits;
        echo 'X', $visits, '|', (int) ($mapWatch->get() !== null), '|',
             (int) ($aWatch->get() === null), '|',
             (int) ($bWatch->get() === null), '|',
             (int) ($cWatch->get() === null), '|',
             (int) ($leafWatch->get() === null), '|';
        if ($visits === 1) { throw new Exception('finite-41'); }
    }
}
$map = new WeakMap;
$k0 = new stdClass;
$k1 = new stdClass;
$k2 = new stdClass;
$k3 = new stdClass;
$a = new GC41PeerManyValue;
$b = new GC41PeerManyValue;
$c = new GC41PeerManyValue;
$leaf = new GC41PeerManyLeaf;
$map[$k0] = $a;
$map[$k1] = $leaf;
$map[$k2] = $b;
$map[$k3] = $c;
$a->child = new GC41PeerManyChild;
$b->child = new GC41PeerManyChild;
$c->child = new GC41PeerManyChild;
$mapWatch = WeakReference::create($map);
$aWatch = WeakReference::create($a);
$bWatch = WeakReference::create($b);
$cWatch = WeakReference::create($c);
$leafWatch = WeakReference::create($leaf);
$visits = 0;
unset($a, $b, $c, $leaf);
echo 'B|';
try { unset($map); echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'A|', $visits, '|', (int) ($mapWatch->get() === null), '|',
     (int) ($aWatch->get() === null), '|',
     (int) ($bWatch->get() === null), '|',
     (int) ($cWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|';
