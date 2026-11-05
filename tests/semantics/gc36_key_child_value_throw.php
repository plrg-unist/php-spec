<?php
class GC36ValueThrow {
    public function __destruct() {
        echo 'VALUE|', (int) ($GLOBALS['keyWatch']->get() !== null), '|';
        throw new Exception('field36');
    }
}
class GC36ChildAfterThrow {
    public function __destruct() {
        echo 'CHILD|', (int) ($GLOBALS['keyWatch']->get() === null), '|';
    }
}
$key = new stdClass;
$map = new WeakMap;
$map[$key] = new GC36ValueThrow;
$key->child = new GC36ChildAfterThrow;
$keyWatch = WeakReference::create($key);
echo 'B|';
try { unset($key); echo 'AFTER|'; }
catch (Throwable $error) { echo 'C|', $error->getMessage(), '|'; }
echo 'A|', (int) ($keyWatch->get() === null), '|';
