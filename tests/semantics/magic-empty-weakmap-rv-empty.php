<?php
class MagicMapParent95 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        global $child;
        echo 'G|';
        $child = null;
        echo 'g|';
        return new WeakMap();
    }
    public function __destruct() { echo 'D|'; }
}
class MagicMapChild95 extends MagicMapParent95 {}
$held = null;
$key = null;
$weak = null;
$child = new MagicMapChild95();
echo 'Z:';
echo empty($child->value) ? 'T' : 'F', '|';
$held = null;
$key = null;
$weak = null;
echo 'E|';
