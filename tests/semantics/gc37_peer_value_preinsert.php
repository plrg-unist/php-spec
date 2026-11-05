<?php
class GC37PeerPreChild {
    public function __destruct() {
        echo 'CHILD|', (int) ($GLOBALS['valueWatch']->get() === null), '|';
    }
}
class GC37PeerPreValue {
    public $child = null;
}
$key = new stdClass;
$map = new WeakMap;
$value = new GC37PeerPreValue;
$valueWatch = WeakReference::create($value);
$value->child = new GC37PeerPreChild;
$map[$key] = $value;
unset($value);
echo 'B|';
unset($key);
echo 'A|', (int) ($valueWatch->get() === null), '|';
