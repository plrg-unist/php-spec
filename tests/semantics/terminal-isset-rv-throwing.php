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
        echo 'I|';
        return [new IssetPayload104()];
    }
    public function __destruct() { echo 'D|'; }
}
class IssetChild104 extends IssetParent104 {}
$error = new Exception('supplied');
$held = null;
$throws = true;
$child = new IssetChild104();
echo 'X:';
$answer = 42;
try {
    $answer = isset($child->value);
} catch (Exception $caught) {
    echo $caught === $error ? 'C' : '!', '|';
}
echo $answer, '|';

$held = null;
$child = null;
echo 'E|';
