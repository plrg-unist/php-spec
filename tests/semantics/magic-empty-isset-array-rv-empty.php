<?php
class IssetArrayParent101 {
    private int $value = 1;
    public function __isset(string $name) {
        global $child;
        echo 'I|';
        $rv = [];
        $rv[] = 7;
        unset($rv[0]);
        $child = null;
        return $rv;
    }
    public function __get($name) {
        echo 'G|';
        throw new Exception('unexpected-array-get');
    }
    public function __destruct() { echo 'D|'; }
}
class IssetArrayChild101 extends IssetArrayParent101 {}
$held = null;
$next = 1;
$child = new IssetArrayChild101();
echo 'F:';
echo empty($child->value) ? 'T' : 'F', '|';
$held = null;
$child = null;
echo 'E|';
