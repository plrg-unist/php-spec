<?php
class CoalesceParent111 {
    private int $value = 41;
    public int $tag = 1;
    public function __isset(string $name): bool { echo 'I', $this->tag, '|'; return false; }
    public function __get($name) { global $error; echo 'G|'; throw $error; }
    public function __set(string $name, $incoming): void {
        global $child, $error, $rhs;
        echo 'S', $this->tag, ':', $incoming, '|';
        $child = null;
        $rhs = 99;
        throw $error;
    }
    public function __destruct() { echo 'D', $this->tag, '|'; }
}
class CoalesceChild111 extends CoalesceParent111 {}
function rhs111(): int { echo 'R|'; return 7; }
$error = new Exception('same111');
$child = new CoalesceChild111();
$rhs = 5;
$result = 42;
echo 'X:';
try { $result = ($child->value ??= rhs111()); echo 'A|'; }
catch (Exception $caught) { if ($caught === $error) { echo 'C|'; } echo $result, '|'; }
echo 'F|';
unset($child, $caught, $error);
echo 'E|';
