<?php
class IssetPayload104 {
    public function __destruct() {
        global $child, $throws, $error;
        echo 'V|';
        $child = null;
        if ($throws) { throw $error; }
        echo 'v|';
    }
}
class IssetParent104 {
    private int $value = 1;
    public function __isset(string $name) {
        global $held;
        echo 'I|';
        $rv = [new IssetPayload104()];
        $held = $rv;
        return $rv;
    }
    public function __get($name) {
        global $error;
        echo 'G|';
        throw $error;
    }
    public function __destruct() { echo 'D|'; }
}
class IssetChild104 extends IssetParent104 {}
$error = new Exception('supplied');
$held = null;
$throws = false;
$child = new IssetChild104();
echo 'H:';
$answer = isset($child->value);
echo $answer ? 'T' : 'F', '|';
echo 'F|';

$held = null;
$child = null;
echo 'E|';
