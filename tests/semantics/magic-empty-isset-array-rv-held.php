<?php
class IssetArrayPayload101 {
    public function __destruct() {
        global $child, $next;
        echo 'V|';
        $child = null;
        $next = 0;
        echo 'v|';
    }
}
class IssetArrayParent101 {
    private int $value = 1;
    public function __isset(string $name) {
        global $held;
        echo 'I|';
        $rv = [new IssetArrayPayload101()];
        $held = $rv;
        return $rv;
    }
    public function __get($name) {
        global $next;
        echo 'G|';
        return $next;
    }
    public function __destruct() { echo 'D|'; }
}
class IssetArrayChild101 extends IssetArrayParent101 {}
$held = null;
$next = 1;
$child = new IssetArrayChild101();
echo 'H:';
echo empty($child->value) ? 'T' : 'F', '|';
$held = null;
$child = null;
echo 'E|';
