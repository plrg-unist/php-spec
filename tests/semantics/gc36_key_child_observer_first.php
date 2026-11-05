<?php
class GC36ValueObserverFirst {
    public function __destruct() {
        echo 'VALUE|', (int) ($GLOBALS['keyWatch']->get() === null), '|';
    }
}
class GC36ChildObserverFirst {
    public function __destruct() {
        echo 'CHILD|', (int) ($GLOBALS['keyWatch']->get() === null), '|';
    }
}
$key = new stdClass;
$map = new WeakMap;
$keyWatch = WeakReference::create($key);
$map[$key] = new GC36ValueObserverFirst;
$key->child = new GC36ChildObserverFirst;
echo 'B|';
unset($key);
echo 'A|', (int) ($keyWatch->get() === null), '|';
