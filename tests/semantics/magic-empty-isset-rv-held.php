<?php
class IssetPayload97 {
    public function __destruct() {
        global $child, $next;
        echo 'V|';
        $child = null;
        $next = 0;
        echo 'v|';
    }
}
class IssetParent97 {
    private int $value = 1;
    public function __isset(string $name) {
        global $held;
        echo 'I|';
        $rv = new IssetPayload97();
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
class IssetChild97 extends IssetParent97 {}
$held = null;
$next = 1;
$child = new IssetChild97();
echo 'H:';
echo empty($child->value) ? 'T' : 'F', '|';
$held = null;
$child = null;
echo 'E|';
