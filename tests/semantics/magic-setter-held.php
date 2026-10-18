<?php
class SetterParent98 {
    private int $value = 1;
    public int $ready = 3;
    public function __set(string $name, $incoming): void {
        global $child, $rhs;
        echo 'S|', $name, '|', $incoming, '|';
        $this->value = $incoming;
        $rhs = 99;
        $child = null;
        echo 's|';
    }
    public function __destruct() {
        global $rhs;
        echo 'D|', $this->value, '|';
        $rhs = 123;
    }
}
class SetterChild98 extends SetterParent98 {}
$rhs = 7;
$child = new SetterChild98();
$child->ready = 5;
$result = 42;
$keep = $child;
echo 'H:';
$result = ($child->value = $rhs);
echo $result, '|', $rhs, '|';
$keep = null;
echo 'Z|', $rhs, '|';
$child = null;
echo 'E|';
