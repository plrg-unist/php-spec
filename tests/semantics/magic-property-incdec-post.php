<?php
class MagicUpdateParent117 {
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
        global $live;
        echo 'D', $this->tag, '/', $this->value, '|';
        $live = 99;
    }
}
class MagicUpdateChild117 extends MagicUpdateParent117 {}
echo 'P:';
$live = 0;
$child = new MagicUpdateChild117();
$result = $child->value++;
echo 'A', $result, '/', $live, '|';
echo 'E|';
