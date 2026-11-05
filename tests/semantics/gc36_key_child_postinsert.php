<?php
class GC36ValuePost {
    public function __destruct() {
        echo 'VALUE|', (int) ($GLOBALS['keyWatch']->get() !== null), '|';
    }
}
class GC36ChildPost {
    public function __destruct() {
        echo 'CHILD|', (int) ($GLOBALS['keyWatch']->get() === null), '|';
    }
}
$key = new stdClass;
$map = new WeakMap;
$map[$key] = new GC36ValuePost;
$key->child = new GC36ChildPost;
$keyWatch = WeakReference::create($key);
echo 'B|';
unset($key);
echo 'A|', (int) ($keyWatch->get() === null), '|';
