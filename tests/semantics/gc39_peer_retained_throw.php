<?php
class GC39PeerValue {
    public $child = null;
}
class GC39PeerChild {
    public function __destruct() {
        echo 'C|',
            (int) ($GLOBALS['mapWatch']->get() === null), '|',
            (int) ($GLOBALS['valueWatch']->get() === null), '|',
            (int) ($GLOBALS['keyWatch']->get() !== null), '|';
        throw new Exception('retained-39');
    }
}
$map = new WeakMap;
$mapWatch = WeakReference::create($map);
$key = new stdClass;
$keyWatch = WeakReference::create($key);
$value = new GC39PeerValue;
$map[$key] = $value;
$valueWatch = WeakReference::create($value);
$child = new GC39PeerChild;
$value->child = $child;
unset($value);
echo 'B|';
unset($map);
echo 'A|',
    (int) ($mapWatch->get() === null), '|',
    (int) ($valueWatch->get() === null), '|',
    (int) ($keyWatch->get() !== null), '|';
try { unset($child); echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'Z|',
    (int) ($mapWatch->get() === null), '|',
    (int) ($valueWatch->get() === null), '|',
    (int) ($keyWatch->get() !== null), '|';
