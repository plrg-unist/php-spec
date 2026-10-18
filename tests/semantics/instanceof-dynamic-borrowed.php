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
function skipped102() { echo "BAD|"; return new Other102; }
$left = new Child102;
$saved = $left;
echo "B:";
$result = $left instanceof (rhs102());
echo $result ? "T|" : "F|";
echo $left instanceof Other102 ? "O|" : "BAD|";
$left = null;
$saved = null;
echo "C|";
echo 7 instanceof (skipped102()) ? "T|" : "F|";
echo "E|";
