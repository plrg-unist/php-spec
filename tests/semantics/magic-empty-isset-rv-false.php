<?php
class IssetParent97 {
    private int $value = 1;
    public function __isset(string $name) {
        global $child;
        echo 'I|';
        $child = null;
        return false;
    }
    public function __get($name) {
        global $next;
        echo 'G|';
        throw new Exception('unexpected-get');
    }
    public function __destruct() { echo 'D|'; }
}
class IssetChild97 extends IssetParent97 {}
$held = null;
$next = 1;
$child = new IssetChild97();
echo 'F:';
echo empty($child->value) ? 'T' : 'F', '|';
$held = null;
$child = null;
echo 'E|';
