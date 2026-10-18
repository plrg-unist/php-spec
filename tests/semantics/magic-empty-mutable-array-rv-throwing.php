<?php
class MutableArrayParent94 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        global $child;
        echo 'G|';
        $a = [new stdClass()];
        $copy = $a;
        unset($copy);
        unset($a[0]);
        $child = null;
        echo 'g|';
        return $a;
    }
    public function __destruct() { echo 'D|'; throw new Exception('mutable-array-stop'); }
}
class MutableArrayChild94 extends MutableArrayParent94 {}
$held = null;
$child = new MutableArrayChild94();
gc_collect_cycles();
echo 'X:';
try { echo empty($child->value) ? 'T' : 'F', '|'; }
catch (Exception $caught) { echo 'C|'; }
$held = null;
echo 'E|';
