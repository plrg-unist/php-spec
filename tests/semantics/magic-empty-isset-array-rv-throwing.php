<?php
class IssetArrayPayload101 {
    public function __destruct() {
        global $child, $next, $error;
        echo 'V|';
        $child = null;
        $next = 0;
        echo 'v|';
        throw $error;
    }
}
class IssetArrayParent101 {
    private int $value = 1;
    public function __isset(string $name) {
        echo 'I|';
        return [new IssetArrayPayload101()];
    }
    public function __get($name) {
        global $next;
        echo 'G|';
        return $next;
    }
    public function __destruct() { echo 'D|'; }
}
class IssetArrayChild101 extends IssetArrayParent101 {}
$error = new Exception('isset-array-stop');
$held = null;
$next = 1;
$child = new IssetArrayChild101();
$answer = 42;
echo 'X:';
try { $answer = empty($child->value); }
catch (Exception $caught) {
    echo 'C|', $answer, '|';
    if ($caught === $error) { echo 'T|'; } else { echo 'F|'; }
}
$held = null;
$child = null;
echo 'E|';
