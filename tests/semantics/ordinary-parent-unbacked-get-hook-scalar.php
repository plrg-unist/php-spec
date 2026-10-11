<?php
class OrdinaryUnbackedParent50 {
    public int $value = 100;
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class OrdinaryUnbackedBridge50 extends OrdinaryUnbackedParent50 {
    private function answer() { return 500; }
}
class OrdinaryUnbackedChild50 extends OrdinaryUnbackedBridge50 {
    public int $value {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
}
class OrdinaryUnbackedGrand50 extends OrdinaryUnbackedChild50 {
    private function answer() { return 900; }
}
$parent = new OrdinaryUnbackedParent50;
$child = new OrdinaryUnbackedChild50;
$grand = new OrdinaryUnbackedGrand50;
echo (array)$parent === ["value" => 100] ? "P100|" : "BAD|";
echo (array)$child === [] ? "CEMPTY|" : "BAD|";
echo (array)$grand === [] ? "GEMPTY|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === [] ? "GEMPTY|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
class OrdinaryUnbackedUntypedParent50 { public $value = 100; }
class OrdinaryUnbackedUntypedChild50 extends OrdinaryUnbackedUntypedParent50 {
    public $value { get { return false; } }
}
$null_parent = new OrdinaryUnbackedUntypedParent50;
$null_child = new OrdinaryUnbackedUntypedChild50;
echo (array)$null_parent === ["value" => 100] ? "NP100|" : "BAD|";
echo (array)$null_child === [] ? "NEMPTY|" : ((array)$null_child === ["value" => null] ? "NNULL|" : "BAD|");
echo $null_child->value === false ? "NFALSE|" : "BAD|";
$null_child->value = 5;
echo (array)$null_child === ["value" => 5] ? "N5|" : "BAD|";
echo $null_child->value === false ? "NFALSE|" : "BAD|";
