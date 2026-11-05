<?php
class GC38PeerThrowValue {
    public $child = null;
}
class GC38PeerThrowChild {
    public function __destruct() {
        echo 'C|',
            (int) ($GLOBALS['mapWatch']->get() !== null), '|',
            (int) ($GLOBALS['valueWatch']->get() === null), '|',
            (int) ($GLOBALS['keyWatch']->get() !== null), '|';
        throw new Exception('map-first-38');
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC38PeerThrowValue;
$value->child = new GC38PeerThrowChild;
$mapWatch = WeakReference::create($map);
$keyWatch = WeakReference::create($key);
$map[$key] = $value;
$valueWatch = WeakReference::create($value);
unset($value);
echo 'B|';
try { unset($map); echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'A|',
    (int) ($mapWatch->get() === null), '|',
    (int) ($valueWatch->get() === null), '|',
    (int) ($keyWatch->get() !== null), '|';
