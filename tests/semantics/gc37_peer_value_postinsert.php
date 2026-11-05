<?php
class GC37PeerPostChild {
    public function __destruct() {
        echo 'CHILD|', (int) ($GLOBALS['valueWatch']->get() === null), '|';
    }
}
class GC37PeerPostValue {
    public $child = null;
}
$key = new stdClass;
$map = new WeakMap;
$value = new GC37PeerPostValue;
$valueWatch = WeakReference::create($value);
$map[$key] = $value;
$value->child = new GC37PeerPostChild;
unset($value);
echo 'B|';
unset($key);
echo 'A|', (int) ($valueWatch->get() === null), '|';
