<?php
class ProtectedSetPlainParent60 {
    public int $value {
        get {
            echo "GET:", self::class, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
    public function parentRead() { echo "H|"; return $this->value; }
    public function putParent($value) {
        echo "PWRITE:", self::class, "/", static::class, "|";
        $this->value = $value;
    }
}
class ProtectedSetPlainBridge60 extends ProtectedSetPlainParent60 {}
class ProtectedSetPlainChild60 extends ProtectedSetPlainBridge60 {
    public protected(set) int $value = 200;
    private function answer() { return 500; }
    public function putChild($value) {
        echo "CWRITE:", self::class, "/", static::class, "|";
        $this->value = $value;
    }
}
class ProtectedSetPlainGrand60 extends ProtectedSetPlainChild60 {
    private function answer() { return 900; }
}
$parent = new ProtectedSetPlainParent60;
$child = new ProtectedSetPlainChild60;
$grand = new ProtectedSetPlainGrand60;
$raw = (array) $parent;
echo $raw === [] ? "EMPTY|" : ($raw === ["value" => null] ? "NULL|" : "BAD|");
$raw = (array) $child;
echo $raw === ["value" => 200] ? "C200|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
try { $grand->value = 999; echo "GBAD|"; }
catch (Error $error) { echo "GLOBAL:", $error->getMessage(), "|"; }
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
$grand->putChild(300);
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
try { $grand->putParent(400); }
catch (Error $error) { echo "PARENT:", $error->getMessage(), "|"; }
$raw = (array) $grand;
echo $raw === ["value" => 400] ? "G400|" : "BAD|";
echo $grand->value, "|";
