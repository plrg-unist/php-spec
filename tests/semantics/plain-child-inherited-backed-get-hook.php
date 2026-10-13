<?php
class PlainInheritedParent54 {
    public int $value = 100 {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class PlainInheritedBridge54 extends PlainInheritedParent54 {}
class PlainInheritedChild54 extends PlainInheritedBridge54 {
    public int $value = 200;
    private function answer() { return 500; }
}
class PlainInheritedGrand54 extends PlainInheritedChild54 {
    private function answer() { return 900; }
}
$parent = new PlainInheritedParent54();
$child = new PlainInheritedChild54();
$grand = new PlainInheritedGrand54();
$raw = (array) $parent;
echo $raw === ["value" => 100] ? "P100|" : "BAD|";
$raw = (array) $child;
echo $raw === ["value" => 200] ? "C200|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
