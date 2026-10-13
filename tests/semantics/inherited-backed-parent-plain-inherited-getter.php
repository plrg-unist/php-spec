<?php
class InheritedPlainRoot57 {
    public int $value = 100 {
        get {
            echo "ROOT:", self::class, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 7; }
}
class InheritedPlainParent57 extends InheritedPlainRoot57 {
    public int $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class InheritedPlainBridge57 extends InheritedPlainParent57 {}
class InheritedPlainChild57 extends InheritedPlainBridge57 {
    public int $value = 200;
    private function answer() { return 500; }
}
class InheritedPlainGrand57 extends InheritedPlainChild57 {
    private function answer() { return 900; }
}
$root = new InheritedPlainRoot57;
$parent = new InheritedPlainParent57;
$child = new InheritedPlainChild57;
$grand = new InheritedPlainGrand57;
$raw = (array) $root;
echo $raw === ["value" => 100] ? "R100|" : "BAD|";
$raw = (array) $parent;
echo $raw === [] ? "EMPTY|" : ($raw === ["value" => null] ? "NULL|" : "BAD|");
$raw = (array) $child;
echo $raw === ["value" => 200] ? "C200|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
echo $root->value, "|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
