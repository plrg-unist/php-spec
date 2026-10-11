<?php
class OrdinaryBackedParent49 {
    public int $value = 100;
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class OrdinaryBackedBridge49 extends OrdinaryBackedParent49 {
    private function answer() { return 500; }
}
class OrdinaryBackedChild49 extends OrdinaryBackedBridge49 {
    public int $value = 200 {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
}
class OrdinaryBackedGrand49 extends OrdinaryBackedChild49 {
    private function answer() { return 900; }
}
$parent = new OrdinaryBackedParent49;
$child = new OrdinaryBackedChild49;
$grand = new OrdinaryBackedGrand49;
echo (array)$parent === ["value" => 100] ? "P100|" : "BAD|";
echo (array)$child === ["value" => 200] ? "C200|" : "BAD|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
