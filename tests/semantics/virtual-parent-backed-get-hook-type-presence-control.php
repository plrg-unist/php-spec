<?php
class CrossBackedParent45 {
    public $value {
        get { echo "P:", __CLASS__, "/", static::class, "|"; return 7; }
    }
    public function parentRead() { echo "H|"; return $this->value; }
}
class CrossBackedBridge45 extends CrossBackedParent45 {
    private function answer() { return 500; }
}
class CrossBackedChild45 extends CrossBackedBridge45 {
    public $value = 200 {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
}
class CrossBackedGrand45 extends CrossBackedChild45 {
    private function answer() { return 900; }
}
$parent = new CrossBackedParent45;
$child = new CrossBackedChild45;
$grand = new CrossBackedGrand45;
echo (array)$parent === [] ? "EMPTY|" : "BAD|";
echo (array)$child === ["value" => 200] ? "C200|" : "BAD|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
