<?php
class MagicArrayParent89 {
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
        return [];
    }
    public function __destruct() { echo 'D|'; }
}
class MagicArrayChild89 extends MagicArrayParent89 {}
$child = new MagicArrayChild89();
echo 'Z:', empty($child->value) ? 'T' : 'F', '|';
echo 'E|';
