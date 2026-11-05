<?php
class GC34SingleIncomingThrow {
    public function __destruct() {
        echo 'M1|';
        throw new Exception('first');
    }
}
$target = new stdClass;
$key = WeakReference::create($target);
$map = new WeakMap;
$map[$key] = new GC34SingleIncomingThrow;
echo 'B|';
try {
    unset($key);
    echo 'AFTER|';
} catch (Throwable $error) {
    echo 'C|', $error->getMessage(), '|';
}
echo 'T|', count($map), '|';
