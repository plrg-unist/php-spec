<?php
class GC42PeerDeepValue { public $a = null; public $b = null; }
class GC42PeerDeepLeaf {}
class GC42PeerDeepHolder { public $child = null; }
class GC42PeerDeepChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$value = new GC42PeerDeepValue;
$leaf = new GC42PeerDeepLeaf;
$map[$firstKey] = $value;
$map[$secondKey] = $leaf;
$holder = new GC42PeerDeepHolder;
$holder->child = new GC42PeerDeepChild;
$value->a = $holder;
$value->b = 7;
unset($value, $leaf, $holder);
echo 'B|';
unset($map);
echo 'A|';
