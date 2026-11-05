<?php
class GC43PeerManyHookValue {
    public $child = null {
        get { echo 'HOOK|'; return $this->child; }
    }
}
class GC43PeerManyHookLeaf {}
class GC43PeerManyHookChild {
    public function __destruct() {
        global $mapWatch, $valueWatch, $leafWatch;
        echo 'C|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($leafWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$value = new GC43PeerManyHookValue;
$leaf = new GC43PeerManyHookLeaf;
$map[$firstKey] = $value;
$map[$secondKey] = $leaf;
$value->child = new GC43PeerManyHookChild;
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$leafWatch = WeakReference::create($leaf);
unset($value, $leaf);
echo 'B|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($leafWatch->get() === null), '|';
