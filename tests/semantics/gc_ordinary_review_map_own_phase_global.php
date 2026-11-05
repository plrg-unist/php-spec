<?php
class GC34OwnViewGlobal {
    public function __destruct() {
        global $watch;
        echo 'OWN|', (int) ($watch->get() !== null), '|';
    }
}
class GC34IncomingViewGlobal {
    public function __destruct() { echo 'IN|'; }
}
$map = new WeakMap;
$watch = WeakReference::create($map);
$key = new stdClass;
$outer = new WeakMap;
$outer[$map] = new GC34IncomingViewGlobal;
$map[$key] = new GC34OwnViewGlobal;
echo 'B|';
unset($map);
echo 'A|', (int) ($watch->get() === null), '|';
