<?php
class StorageBodyParent46 {
    public $value = 100 {
        get { echo "P:", __CLASS__, "/", static::class, "|"; return $this->value; }
    }
    public function parentRead() { echo "H|"; return $this->value; }
}
class StorageBodyBridge46 extends StorageBodyParent46 {
    private function answer() { return 500; }
}
class StorageBodyChild46 extends StorageBodyBridge46 {
    public $value {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
}
class StorageBodyGrand46 extends StorageBodyChild46 {
    private function answer() { return 900; }
}
$parent = new StorageBodyParent46;
$child = new StorageBodyChild46;
$grand = new StorageBodyGrand46;
echo (array)$parent === ["value" => 100] ? "P100|" : "BAD|";
echo (array)$child === ["value" => null] ? "CNULL|" : "BAD|";
echo (array)$grand === ["value" => null] ? "GNULL|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === ["value" => null] ? "GNULL|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
