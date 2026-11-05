<?php
class GC34SelfCreate {
    public function __destruct() {
        global $keyWatch;
        $old = $keyWatch->get();
        echo 'V|', (int) ($old !== null), '|';
        $again = WeakReference::create($old);
        echo (int) ($again === $keyWatch), '|', (int) ($old->get() === null), '|';
    }
}
$target = new stdClass;
$key = WeakReference::create($target);
$map = new WeakMap;
$map[$key] = new GC34SelfCreate;
$keyWatch = WeakReference::create($key);
echo 'B|';
unset($key);
echo 'A|', (int) ($keyWatch->get() === null), '|';
