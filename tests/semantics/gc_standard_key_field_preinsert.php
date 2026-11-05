<?php
class GC36PreValue {
    public function __destruct() {
        echo 'V|', $GLOBALS['gc36Watch']->get() === null ? 'N' : 'L', '|';
    }
}
class GC36PreChild {
    public function __destruct() {
        echo 'C|', $GLOBALS['gc36Watch']->get() === null ? 'N' : 'L', '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$key->child = new GC36PreChild;
$map[$key] = new GC36PreValue;
$watch = WeakReference::create($key);
$GLOBALS['gc36Watch'] = $watch;
echo 'B|';
unset($key);
echo 'A|';
