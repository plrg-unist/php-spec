<?php
class GC49PeerOld { public $a = null; public $b = null; public $c = null; }
class GC49PeerOther { public $child = null; }
class GC49PeerX {
    public function __destruct() {
        global $map, $key, $otherKey, $otherWatch;
        echo 'X|', (int) ($map[$key] === 0), '|',
             (int) ($map[$otherKey] === $otherWatch->get()), '|';
    }
}
class GC49PeerY {
    public function __destruct() {
        global $map, $key, $otherKey, $oldWatch, $otherWatch;
        echo 'Y|', (int) ($oldWatch->get() === null), '|',
             (int) ($map[$key] === 0), '|',
             (int) ($map[$otherKey] === $otherWatch->get()), '|';
    }
}
class GC49PeerZ {
    public function __destruct() {
        global $map, $key, $otherWatch;
        echo 'Z|', (int) ($map[$key] === 0), '|',
             (int) ($otherWatch->get() === null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$otherKey = new stdClass;
$old = new GC49PeerOld;
$x = new GC49PeerX;
$y = new GC49PeerY;
$old->c = $x;
$old->b = $y;
$old->a = $x;
$other = new GC49PeerOther;
$z = new GC49PeerZ;
$other->child = $z;
$map[$key] = $old;
$map[$otherKey] = $other;
$oldWatch = WeakReference::create($old);
$otherWatch = WeakReference::create($other);
unset($old, $x, $y, $other, $z);
$held = $map[$key];
echo 'B|';
$written = $map[$key] = 0;
echo 'R|', (int) ($written === 0), '|',
     (int) ($map[$key] === 0), '|',
     (int) isset($map[$key]), '|', (int) empty($map[$key]), '|';
echo 'H|', (int) ($oldWatch->get() === $held), '|';
unset($held);
echo 'V|', (int) ($oldWatch->get() === null), '|',
     (int) ($otherWatch->get() !== null), '|';
unset($otherKey);
echo 'N|', (int) ($otherWatch->get() === null), '|',
     (int) isset($map[$key]), '|', (int) empty($map[$key]), '|';
unset($map);
echo 'A|', (int) ($oldWatch->get() === null), '|',
     (int) ($otherWatch->get() === null), '|';
