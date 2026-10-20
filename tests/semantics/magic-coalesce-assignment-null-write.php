<?php
class CoalesceParent111 {
    private int $value = 41;
    public int $tag = 1;
    public function __isset(string $name): bool { echo 'I', $this->tag, '|'; return true; }
    public function __get($name) { echo 'G', $this->tag, '|'; return null; }
    public function __set(string $name, $incoming): void { global $error; echo 'S|'; throw $error; }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
class CoalesceChild111 extends CoalesceParent111 {}
function rhs111(): int {
    global $child;
    echo 'R|';
    $child = null;
    echo 'r|';
    return 7;
}
$error = new Exception('same111');
$child = new CoalesceChild111();
$result = 42;
echo 'E:';
try { $result = ($child->value ??= rhs111()); echo 'A|'; }
catch (Error $caught) { echo 'C|', $caught->getMessage(), '|', $result, '|'; }
echo 'F|';
unset($child, $caught, $error);
echo 'E|';
