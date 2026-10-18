<?php
class IssetParent104 {
    private int $value = 1;
    public function __isset(string $name) {
        global $child;
        echo 'I|';
        $child = null;
        $rv = [];
        $rv[] = 1;
        unset($rv[0]);
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
echo 'F:';
$answer = isset($child->value);
echo $answer ? 'T' : 'F', '|';

$held = null;
$child = null;
echo 'E|';
