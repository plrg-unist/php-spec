<?php
class GC34OldGetBeforeObserver {
    public function __destruct() {
        global $keyWatch, $target;
        $old = $keyWatch->get();
        $GLOBALS['newWR34'] = WeakReference::create($target);
        echo 'V|', (int) ($old !== null), '|', (int) ($old?->get() === $target), '|',
            (int) ($GLOBALS['newWR34'] !== $old), '|';
    }
}
$target = new stdClass;
$key = WeakReference::create($target);
$map = new WeakMap;
$map[$key] = new GC34OldGetBeforeObserver;
$keyWatch = WeakReference::create($key);
echo 'B|';
unset($key);
echo 'A|', (int) ($keyWatch->get() === null), '|',
    (int) ($GLOBALS['newWR34']->get() === $target), '|';
