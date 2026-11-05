<?php
class GC41PeerExtraValue { public $child = null; public $other = null; }
class GC41PeerExtraLeaf {}
class GC41PeerExtraChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$field = new GC41PeerExtraValue;
$leaf = new GC41PeerExtraLeaf;
$map[$firstKey] = $field;
$map[$secondKey] = $leaf;
$field->child = new GC41PeerExtraChild;
unset($field, $leaf);
echo 'B|';
unset($map);
echo 'A|';
