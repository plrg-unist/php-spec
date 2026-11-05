<?php
class GC48PeerOldValue { public $a = null; public $b = null; public $c = null; }
class GC48PeerNewValue { public $child = null; }
class GC48PeerLeaf {}
class GC48PeerX {
    public function __destruct() {
        global $map, $key, $mapWatch, $keyWatch, $oldWatch, $newWatch, $yWatch, $zWatch, $leftWatch, $rightWatch;
        echo 'X|', (int) ($mapWatch->get() !== null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($oldWatch->get() === null), '|',
             (int) ($map[$key] === $newWatch->get()), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($zWatch->get() !== null), '|',
             (int) ($leftWatch->get() !== null), '|',
             (int) ($rightWatch->get() !== null), '|';
    }
}
class GC48PeerY {
    public function __destruct() {
        global $map, $key, $mapWatch, $keyWatch, $oldWatch, $newWatch, $xWatch, $zWatch, $leftWatch, $rightWatch;
        echo 'Y|', (int) ($mapWatch->get() !== null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($oldWatch->get() === null), '|',
             (int) ($map[$key] === $newWatch->get()), '|',
             (int) ($xWatch->get() !== null), '|',
             (int) ($zWatch->get() !== null), '|',
             (int) ($leftWatch->get() !== null), '|',
             (int) ($rightWatch->get() !== null), '|';
    }
}
class GC48PeerZ {
    public function __destruct() {
        global $mapWatch, $keyWatch, $oldWatch, $newWatch, $xWatch, $yWatch, $leftWatch, $rightWatch;
        echo 'Z|', (int) ($mapWatch->get() !== null), '|',
             (int) ($keyWatch->get() !== null), '|',
             (int) ($oldWatch->get() === null), '|',
             (int) ($newWatch->get() === null), '|',
             (int) ($xWatch->get() === null), '|',
             (int) ($yWatch->get() === null), '|',
             (int) ($leftWatch->get() !== null), '|',
             (int) ($rightWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$leftKey = new stdClass;
$rightKey = new stdClass;
$old = new GC48PeerOldValue;
$x = new GC48PeerX;
$y = new GC48PeerY;
$old->c = $x;
$old->b = $y;
$old->a = $x;
$replacement = new GC48PeerNewValue;
$z = new GC48PeerZ;
$replacement->child = $z;
$left = new GC48PeerLeaf;
$right = new GC48PeerLeaf;
$map[$key] = $old;
$map[$leftKey] = $left;
$map[$rightKey] = $right;
$mapWatch = WeakReference::create($map);
$keyWatch = WeakReference::create($key);
$oldWatch = WeakReference::create($old);
$newWatch = WeakReference::create($replacement);
$xWatch = WeakReference::create($x);
$yWatch = WeakReference::create($y);
$zWatch = WeakReference::create($z);
$leftWatch = WeakReference::create($left);
$rightWatch = WeakReference::create($right);
unset($old, $x, $y, $z, $left, $right);
$held = $map[$key];
echo 'B|';
$written = $map[$key] = $replacement;
echo 'R|', (int) ($written === $replacement), '|',
     (int) ($map[$key] === $written), '|';
unset($replacement, $written);
echo 'H|', (int) ($oldWatch->get() === $held), '|',
     (int) ($xWatch->get() !== null), '|',
     (int) ($yWatch->get() !== null), '|',
     (int) ($newWatch->get() !== null), '|',
     (int) ($zWatch->get() !== null), '|';
unset($held);
echo 'V|', (int) ($oldWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($newWatch->get() !== null), '|',
     (int) ($zWatch->get() !== null), '|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($oldWatch->get() === null), '|',
     (int) ($newWatch->get() === null), '|',
     (int) ($xWatch->get() === null), '|',
     (int) ($yWatch->get() === null), '|',
     (int) ($zWatch->get() === null), '|',
     (int) ($leftWatch->get() === null), '|',
     (int) ($rightWatch->get() === null), '|',
     (int) ($keyWatch->get() !== null), '|';
