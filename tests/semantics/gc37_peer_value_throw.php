<?php
class GC37PeerThrowChild {
    public function __destruct() {
        echo 'CHILD|', (int) ($GLOBALS['valueWatch']->get() === null), '|';
        throw new Exception('value-child-37');
    }
}
class GC37PeerThrowValue {
    public $child = null;
}
$key = new stdClass;
$map = new WeakMap;
$value = new GC37PeerThrowValue;
$valueWatch = WeakReference::create($value);
$value->child = new GC37PeerThrowChild;
$map[$key] = $value;
unset($value);
echo 'B|';
try { unset($key); echo 'AFTER|'; }
catch (Throwable $error) { echo 'C|', $error->getMessage(), '|'; }
echo 'A|', (int) ($valueWatch->get() === null), '|';
