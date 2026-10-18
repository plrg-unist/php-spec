<?php
class MutableArrayParent94 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        global $child, $held;
        echo 'G|';
        $a = [new stdClass()];
        $copy = $a;
        unset($copy);
        unset($a[0]);
        $held = $a;
        $child = null;
        echo 'g|';
        return $a;
    }
    public function __destruct() { echo 'D|'; }
}
class MutableArrayChild94 extends MutableArrayParent94 {}
$held = null;
$child = new MutableArrayChild94();
gc_collect_cycles();
echo 'H:';
echo empty($child->value) ? 'T' : 'F', '|';
$held = null;
echo 'E|';
