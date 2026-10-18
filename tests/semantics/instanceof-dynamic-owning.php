<?php
class Base102 {}
class Other102 {}
class Child102 extends Base102 {
    public int $role = 0;
    public function __toString(): string { echo "BAD|"; return "Other102"; }
    public function __destruct() {
        global $left;
        if ($this->role === 1) { echo "R|"; $left = new Other102; }
        else { echo "L|"; }
    }
}
function rhs102() {
    echo "r|";
    $object = new Child102;
    $object->role = 1;
    return $object;
}
function lhs102() { echo "l|"; return new Child102; }
$left = null;
echo "T:";
$result = (lhs102()) instanceof (rhs102());
echo $result ? "T|" : "F|";
echo $left instanceof Other102 ? "O|" : "BAD|";
$left = null;
echo "E|";
