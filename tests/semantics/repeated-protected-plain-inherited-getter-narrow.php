<?php
class RepeatedProtectedNarrowParent62 {
    public int $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class RepeatedProtectedNarrowFirst62 extends RepeatedProtectedNarrowParent62 {
    public protected(set) int $value = 200;
    private function answer() { return 500; }
}
class RepeatedProtectedNarrowBridge62 extends RepeatedProtectedNarrowFirst62 {}
class RepeatedProtectedNarrowSecond62 extends RepeatedProtectedNarrowBridge62 {
    public private(set) int $value = 300;
    private function answer() { return 700; }
    public function write($value) {
        echo "WRITE:", self::class, "/", static::class, "|";
        $this->value = $value;
    }
}
class RepeatedProtectedNarrowGrand62 extends RepeatedProtectedNarrowSecond62 {
    private function answer() { return 900; }
}
$parent = new RepeatedProtectedNarrowParent62;
$first = new RepeatedProtectedNarrowFirst62;
$second = new RepeatedProtectedNarrowSecond62;
$grand = new RepeatedProtectedNarrowGrand62;
$raw = (array) $parent;
echo $raw === [] ? "EMPTY|" : ($raw === ["value" => null] ? "NULL|" : "BAD|");
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
try { $grand->value = 999; } catch (Error $error) { echo "GLOBAL:", $error->getMessage(), "|"; }
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
$grand->write(400);
$raw = (array) $grand;
echo $raw === ["value" => 400] ? "G400|" : "BAD|";
echo $grand->value, "|";
