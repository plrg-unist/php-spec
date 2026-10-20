<?php
class MagicAddParent115 {
    private int $value = 5;
    public int $tag = 1;
    public function __get($name) {
        global $child;
        echo 'G', $this->tag, '|', __CLASS__, '|', static::class, '|';
        $child = null;
        echo 'g|';
        return $this->value;
    }
    public function __set(string $name, $incoming): void {
        global $error;
        echo 'S', $this->tag, '/', $incoming, '|';
        throw $error;
    }
    public function __destruct() {
        global $rhs;
        echo 'D', $this->tag, '/', $this->value, '|';
        $rhs = 99;
    }
}
class MagicAddChild115 extends MagicAddParent115 {}
function rhs115(): int {
    global $rhs;
    echo 'R|';
    $rhs = 55;
    echo 'r|';
    return 2;
}
echo 'X:';
$error = new Exception('chosen115');
$rhs = 0;
$result = 42;
$child = new MagicAddChild115();
try {
    $result = ($child->value += rhs115());
    echo 'BAD|';
} catch (Exception $caught) {
    if ($caught === $error) { echo 'C|'; }
    echo $result, '/', $rhs, '|';
} finally { echo 'F|'; }
echo 'E|';
