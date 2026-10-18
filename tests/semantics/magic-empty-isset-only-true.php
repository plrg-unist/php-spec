<?php
class MagicIssetOnlyParent90 {
    private int $value = 1;
    public function __isset(string $name): bool {
        global $child;
        echo 'I|';
        $child = null;
        echo 'i|';
        return true;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicIssetOnlyChild90 extends MagicIssetOnlyParent90 {}
$child = new MagicIssetOnlyChild90();
echo 'T:', empty($child->value) ? 'T' : 'F', '|';
echo 'E|';
