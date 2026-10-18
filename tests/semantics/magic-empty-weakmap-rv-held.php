<?php
class MapPayload95 {
    public function __destruct() {
        global $child, $key, $weak;
        echo 'V|';
        $key = null;
        echo $weak->get() === null ? 'K' : 'k', '|';
        $child = null;
        echo 'v|';
    }
}
class MagicMapParent95 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        global $key, $held;
        echo 'G|';
        $map = new WeakMap();
        $map[$key] = new MapPayload95();
        $held = $map;
        return $map;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicMapChild95 extends MagicMapParent95 {}
$held = null;
$key = null;
$weak = null;
$key = new stdClass();
$weak = WeakReference::create($key);
$child = new MagicMapChild95();
echo 'H:';
echo empty($child->value) ? 'T' : 'F', '|';
$held = null;
$key = null;
$weak = null;
echo 'E|';
