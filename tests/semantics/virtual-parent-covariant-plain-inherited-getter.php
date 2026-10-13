<?php
class CovariantPlainParent59 {
    public mixed $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return "13"; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class CovariantPlainBridge59 extends CovariantPlainParent59 {}
class CovariantPlainChild59 extends CovariantPlainBridge59 {
    public int $value = 200;
    private function answer() { return 500; }
}
class CovariantPlainGrand59 extends CovariantPlainChild59 {
    private function answer() { return 900; }
}
$parent = new CovariantPlainParent59;
$child = new CovariantPlainChild59;
$grand = new CovariantPlainGrand59;
$raw = (array) $parent;
echo $raw === [] ? "EMPTY|" : ($raw === ["value" => null] ? "NULL|" : "BAD|");
$raw = (array) $child;
echo $raw === ["value" => 200] ? "C200|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
$result = $child->value;
echo $result === "13" ? "CS|" : "BAD|";
echo $grand->parentRead(), "|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
$result = $grand->value;
echo $result === "13" ? "GS|" : "BAD|";
