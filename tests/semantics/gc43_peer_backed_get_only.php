<?php
class GC43PeerHookValue {
    public $child = null { get => $this->child; }
}
class GC43PeerHookChild {
    public function __destruct() { echo 'C|'; }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC43PeerHookValue;
$map[$key] = $value;
$value->child = new GC43PeerHookChild;
unset($value);
echo 'B|';
unset($map);
echo 'A|';
