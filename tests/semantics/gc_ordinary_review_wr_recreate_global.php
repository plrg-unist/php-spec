<?php
class GC34RecreateGlobal {
    public function __destruct() {
        global $target, $watch;
        echo 'V|', (int) ($watch->get() === null), '|';
        $GLOBALS['newWR34'] = WeakReference::create($target);
        echo (int) ($GLOBALS['newWR34']->get() === $target), '|';
    }
}
$target = new stdClass;
$key = WeakReference::create($target);
$watch = WeakReference::create($key);
$map = new WeakMap;
$map[$key] = new GC34RecreateGlobal;
echo 'B|';
unset($key);
echo 'A|', (int) ($GLOBALS['newWR34']->get() === $target), '|', (int) ($watch->get() === null), '|';
