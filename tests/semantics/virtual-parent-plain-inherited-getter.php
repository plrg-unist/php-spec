<?php
class VirtualPlainParent58 {
    public int $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class VirtualPlainBridge58 extends VirtualPlainParent58 {}
class VirtualPlainChild58 extends VirtualPlainBridge58 {
    public int $value = 200;
    private function answer() { return 500; }
}
class VirtualPlainGrand58 extends VirtualPlainChild58 {
    private function answer() { return 900; }
}
$parent = new VirtualPlainParent58;
$child = new VirtualPlainChild58;
$grand = new VirtualPlainGrand58;
$raw = (array) $parent;
echo $raw === [] ? "EMPTY|" : ($raw === ["value" => null] ? "NULL|" : "BAD|");
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
