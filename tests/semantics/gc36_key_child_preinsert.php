<?php
class GC36ValuePre {
    public function __destruct() {
        echo 'VALUE|', (int) ($GLOBALS['keyWatch']->get() !== null), '|';
    }
}
class GC36ChildPre {
    public function __destruct() {
        echo 'CHILD|', (int) ($GLOBALS['keyWatch']->get() === null), '|';
    }
}
$key = new stdClass;
$key->child = new GC36ChildPre;
$map = new WeakMap;
$map[$key] = new GC36ValuePre;
$keyWatch = WeakReference::create($key);
echo 'B|';
unset($key);
echo 'A|', (int) ($keyWatch->get() === null), '|';
