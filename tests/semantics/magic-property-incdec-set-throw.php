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
        global $error;
        echo 'S', $this->tag, '/', $incoming, '|';
        $this->value = $incoming;
        echo 't|';
        throw $error;
    }
    public function __destruct() {
        global $live;
        echo 'D', $this->tag, '/', $this->value, '|';
        $live = 99;
    }
}
class MagicUpdateChild117 extends MagicUpdateParent117 {}
$error = new Exception('planned117');
$after = 42;
$live = 0;
echo 'X:';
$child = new MagicUpdateChild117();
try { $after = ++$child->value; echo 'bad|'; }
catch (Throwable $caught) {
    echo 'C|', $caught === $error ? 'same|' : 'wrong|', $after, '/', $live, '|';
}
unset($caught, $error);
echo 'E|';
