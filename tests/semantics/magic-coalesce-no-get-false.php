<?php
class CoalesceParent106 {
    private int $value = 1;
    public function __isset(string $name): bool {
        global $child, $held;
        echo 'I|';
        $child = null;
        return false;
    }
    public function __destruct() {
        global $fallback;
        echo 'D|';
        $fallback = 99;
    }
}
class CoalesceChild106 extends CoalesceParent106 {}
function fallback106() {
    global $fallback;
    echo 'R|';
    return $fallback;
}
$error = new Exception('supplied');
$held = null;
$throws = false;
$fallback = 7;
$child = new CoalesceChild106();
$weak = WeakReference::create($child);
$result = 42;
echo 'F:';
try {
    $result = $child->value ?? fallback106();
} catch (Exception $caught) {
    echo $caught === $error ? 'C' : '!', '|';
}
echo $result, '|';
echo 'F|';
$held = null;
$child = null;
echo 'E|';
