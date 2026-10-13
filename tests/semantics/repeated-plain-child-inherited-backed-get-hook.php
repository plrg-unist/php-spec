<?php
class RepeatedPlainParent55 {
    public int $value = 100 {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class RepeatedPlainFirst55 extends RepeatedPlainParent55 {
    public int $value = 200;
    private function answer() { return 500; }
}
class RepeatedPlainBridge55 extends RepeatedPlainFirst55 {}
class RepeatedPlainSecond55 extends RepeatedPlainBridge55 {
    public int $value = 300;
    private function answer() { return 700; }
}
class RepeatedPlainGrand55 extends RepeatedPlainSecond55 {
    private function answer() { return 900; }
}
$parent = new RepeatedPlainParent55;
$first = new RepeatedPlainFirst55;
$second = new RepeatedPlainSecond55;
$grand = new RepeatedPlainGrand55;
$raw = (array) $parent;
echo $raw === ["value" => 100] ? "P100|" : "BAD|";
$raw = (array) $first;
echo $raw === ["value" => 200] ? "F200|" : "BAD|";
$raw = (array) $second;
echo $raw === ["value" => 300] ? "S300|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $parent->value, "|";
echo $first->value, "|";
echo $second->value, "|";
echo $grand->parentRead(), "|";
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
$grand->value = 400;
$raw = (array) $grand;
echo $raw === ["value" => 400] ? "G400|" : "BAD|";
echo $grand->value, "|";
