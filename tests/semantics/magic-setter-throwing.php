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
        throw new Exception('setter-stop');
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
echo 'X:';
try {
    $result = ($child->value = $rhs);
} catch (Exception $caught) {
    echo 'C|', $result, '|', $rhs, '|';
}
$child = null;
echo 'E|';
