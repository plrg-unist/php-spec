<?php
class OrdinaryPlainRoot56 {
    public int $value = 100;
}
class OrdinaryPlainParent56 extends OrdinaryPlainRoot56 {
    public int $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class OrdinaryPlainBridge56 extends OrdinaryPlainParent56 {}
class OrdinaryPlainChild56 extends OrdinaryPlainBridge56 {
    public int $value = 200;
    private function answer() { return 500; }
}
class OrdinaryPlainGrand56 extends OrdinaryPlainChild56 {
    private function answer() { return 900; }
}
$root = new OrdinaryPlainRoot56;
$parent = new OrdinaryPlainParent56;
$child = new OrdinaryPlainChild56;
$grand = new OrdinaryPlainGrand56;
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
