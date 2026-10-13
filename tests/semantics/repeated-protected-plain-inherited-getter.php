<?php
class RepeatedProtectedPlainParent62 {
    public int $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
}
class RepeatedProtectedPlainFirst62 extends RepeatedProtectedPlainParent62 {
    public protected(set) int $value = 200;
    private function answer() { return 500; }
}
class RepeatedProtectedPlainBridge62 extends RepeatedProtectedPlainFirst62 {}
class RepeatedProtectedPlainSecond62 extends RepeatedProtectedPlainBridge62 {
    public protected(set) int $value = 300;
    private function answer() { return 700; }
    public function write($value) {
        echo "WRITE:", self::class, "/", static::class, "|";
        $this->value = $value;
    }
}
class RepeatedProtectedPlainGrand62 extends RepeatedProtectedPlainSecond62 {
    private function answer() { return 900; }
}
$parent = new RepeatedProtectedPlainParent62;
$first = new RepeatedProtectedPlainFirst62;
$second = new RepeatedProtectedPlainSecond62;
$grand = new RepeatedProtectedPlainGrand62;
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
