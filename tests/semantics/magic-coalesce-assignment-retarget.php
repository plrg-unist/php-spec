<?php
class CoalesceParent111 {
    private int $value = 41;
    public int $tag = 1;
    public function __isset(string $name): bool { echo 'I', $this->tag, '|'; return false; }
    public function __get($name) { global $error; echo 'G|'; throw $error; }
    public function __set(string $name, $incoming): void {
        global $child, $rhs;
        echo 'S', $this->tag, ':', $incoming, '|';
        $this->value = $incoming;
        $rhs = 99;
        $child = null;
    }
    public function peek(): int { return $this->value; }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
class CoalesceChild111 extends CoalesceParent111 {}
function rhs111(): int {
    global $child, $replacement;
    echo 'R|';
    $child = $replacement;
    echo 'r|';
    return 7;
}
$error = new Exception('same111');
$replacement = new CoalesceChild111();
$replacement->tag = 2;
$child = new CoalesceChild111();
$rhs = 5;
$result = 42;
echo 'N:';
$result = ($child->value ??= rhs111());
echo 'A|', $result, '|', $rhs, '|', $replacement->peek(), '|';
unset($child, $replacement, $error);
echo 'E|';
