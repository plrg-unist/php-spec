<?php
class CoalesceParent111 {
    private int $value = 41;
    public int $tag = 1;
    public function __isset(string $name): bool { echo 'I', $this->tag, '|'; return true; }
    public function __get($name) {
        global $child;
        echo 'G', $this->tag, '|';
        $child = null;
        return 0;
    }
    public function __set(string $name, $incoming): void { global $error; echo 'S|'; throw $error; }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
class CoalesceChild111 extends CoalesceParent111 {}
function rhs111(): int { global $error; echo 'R|'; throw $error; }
$error = new Exception('same111');
$child = new CoalesceChild111();
$result = 42;
echo 'Z:';
$result = ($child->value ??= rhs111());
echo 'A|', $result, '|';
unset($child, $error);
echo 'E|';
