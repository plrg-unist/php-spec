<?php
class GC38PeerValue {
    public $child = null;
}
class GC38PeerChild {
    public function __destruct() {
        echo 'C|',
            (int) ($GLOBALS['mapWatch']->get() !== null), '|',
            (int) ($GLOBALS['valueWatch']->get() === null), '|',
            (int) ($GLOBALS['keyWatch']->get() !== null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC38PeerValue;
$value->child = new GC38PeerChild;
$mapWatch = WeakReference::create($map);
$keyWatch = WeakReference::create($key);
$map[$key] = $value;
$valueWatch = WeakReference::create($value);
unset($value);
echo 'B|';
unset($map);
echo 'A|',
    (int) ($mapWatch->get() === null), '|',
    (int) ($valueWatch->get() === null), '|',
    (int) ($keyWatch->get() !== null), '|';
