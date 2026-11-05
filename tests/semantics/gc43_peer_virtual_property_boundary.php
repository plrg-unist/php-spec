<?php
class GC43PeerVirtualValue {
    public $view { get { echo 'HOOK|'; return 7; } }
    public $child = null;
}
class GC43PeerVirtualLeaf {}
class GC43PeerVirtualChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$value = new GC43PeerVirtualValue;
$leaf = new GC43PeerVirtualLeaf;
$map[$firstKey] = $value;
$map[$secondKey] = $leaf;
$value->child = new GC43PeerVirtualChild;
unset($value, $leaf);
echo 'B|';
unset($map);
echo 'A|';
