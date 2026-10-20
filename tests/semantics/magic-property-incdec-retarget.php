<?php
class MagicUpdateParent117 {
    private int $value = 5;
    public int $tag = 1;
    public function __get($name) {
        global $child, $replacement;
        echo 'G', $this->tag, '|', __CLASS__, '|', static::class, '|';
        $child = $replacement;
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
echo 'N:';
$live = 0;
$child = new MagicUpdateChild117();
$replacement = new MagicUpdateChild117();
$replacement->tag = 2;
$result = --$child->value;
echo 'A', $result, '/', $live, '|';
unset($child, $replacement);
echo 'E|';
