<?php
class GC36PostValue {
    public function __destruct() {
        echo 'V|', $GLOBALS['gc36Watch']->get() === null ? 'N' : 'L', '|';
    }
}
class GC36PostChild {
    public function __destruct() {
        echo 'C|', $GLOBALS['gc36Watch']->get() === null ? 'N' : 'L', '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$map[$key] = new GC36PostValue;
$key->child = new GC36PostChild;
$watch = WeakReference::create($key);
$GLOBALS['gc36Watch'] = $watch;
echo 'B|';
unset($key);
echo 'A|';
