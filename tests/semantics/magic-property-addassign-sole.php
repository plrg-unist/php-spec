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
echo 'O:';
$rhs = 0;
$result = 42;
$child = new MagicAddChild115();
$result = ($child->value += rhs115());
echo 'A|', $result, '/', $rhs, '|';
echo 'E|';
