<?php
class CovBackedParent44 {
    public int|string $value {
        get { echo "P:", __CLASS__, "/", static::class, "|"; return "root"; }
    }
    public function parentRead() { echo "H|"; return $this->value; }
}
class CovBackedBridge44 extends CovBackedParent44 {
    private function answer() { return 500; }
}
class CovBackedChild44 extends CovBackedBridge44 {
    public int $value = 200 {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
}
class CovBackedGrand44 extends CovBackedChild44 {
    private function answer() { return 900; }
}
function covBackedBadRhs44() { echo "R|"; return "bad"; }
$parent = new CovBackedParent44;
$child = new CovBackedChild44;
$grand = new CovBackedGrand44;
echo (array)$parent === [] ? "EMPTY|" : "BAD|";
echo (array)$child === ["value" => 200] ? "C200|" : "BAD|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
try { $grand->value = covBackedBadRhs44(); }
catch (TypeError $error) { echo $error->getMessage(), ":", $error->getLine(), "|"; }
echo (array)$grand === ["value" => 300] ? "UNCHANGED|" : "BAD|";
echo $grand->value, "|";
