<?php
class MagicAddParent115 {
    private int $value = 5;
    public int $tag = 1;
    public function __get($name) {
        global $child, $error;
        echo 'G', $this->tag, '|', __CLASS__, '|', static::class, '|';
        $child = null;
        throw $error;
    }
    public function __set(string $name, $incoming): void {
        echo 'S', $this->tag, '/', $incoming, '|';
        $this->value = $incoming;
        echo 's|';
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
echo 'G:';
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
