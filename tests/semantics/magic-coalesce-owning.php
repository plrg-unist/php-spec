<?php
class CoalescePayload105 {
    public function __destruct() { echo 'P|'; }
}
class CoalesceParent105 {
    private int $value = 1;
    public function __isset(string $name): bool {
        global $child;
        echo 'I|';
        $child = null;
        return true;
    }
    public function __get($name) {
        global $error;
        echo 'G|';
        return new CoalescePayload105();
    }
    public function __destruct() {
        global $fallback;
        echo 'D|';
        $fallback = 99;
    }
}
class CoalesceChild105 extends CoalesceParent105 {}
function fallback105() {
    global $fallback, $error;
    echo 'R|';
    throw $error;
}
$error = new Exception('supplied');
$fallback = 7;
$child = new CoalesceChild105();
$result = 42;
echo 'O:';
try {
    $result = $child->value ?? fallback105();
} catch (Exception $caught) {
    echo $caught === $error ? 'C' : '!', '|';
}
echo 'A|';
$result = null;
$child = null;
echo 'E|';
