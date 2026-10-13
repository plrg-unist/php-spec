<?php
class OrdinaryRepeatRoot51 {
    public int $value = 100;
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class OrdinaryRepeatFirst51 extends OrdinaryRepeatRoot51 {
    public int $value {
        get {
            echo "F:", __CLASS__, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 7; }
}
class OrdinaryRepeatBridge51 extends OrdinaryRepeatFirst51 {
    private function answer() { return 500; }
}
class OrdinaryRepeatSecond51 extends OrdinaryRepeatBridge51 {
    public int $value {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
}
class OrdinaryRepeatGrand51 extends OrdinaryRepeatSecond51 {
    private function answer() { return 900; }
}
$root = new OrdinaryRepeatRoot51;
$first = new OrdinaryRepeatFirst51;
$second = new OrdinaryRepeatSecond51;
$grand = new OrdinaryRepeatGrand51;
echo (array)$root === ["value" => 100] ? "P100|" : "BAD|";
echo (array)$first === [] ? "FEMPTY|" : "BAD|";
echo (array)$second === [] ? "CEMPTY|" : "BAD|";
echo (array)$grand === [] ? "GEMPTY|" : "BAD|";
echo $root->value, "|";
echo $first->value, "|";
echo $second->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === [] ? "GEMPTY|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
class OrdinaryRepeatUntypedRoot51 {
    public $value = 100;
    public function parentRead() { return $this->value; }
}
class OrdinaryRepeatUntypedFirst51 extends OrdinaryRepeatUntypedRoot51 {
    public $value { get { return $this->answer(); } }
    private function answer() { return false; }
}
class OrdinaryRepeatUntypedBridge51 extends OrdinaryRepeatUntypedFirst51 {
    private function answer() { return 500; }
}
class OrdinaryRepeatUntypedSecond51 extends OrdinaryRepeatUntypedBridge51 {
    public $value { get { return $this->answer(); } }
    private function answer() { return 0; }
}
class OrdinaryRepeatUntypedGrand51 extends OrdinaryRepeatUntypedSecond51 {
    private function answer() { return 900; }
}
$null_root = new OrdinaryRepeatUntypedRoot51;
$null_first = new OrdinaryRepeatUntypedFirst51;
$null_second = new OrdinaryRepeatUntypedSecond51;
$null_grand = new OrdinaryRepeatUntypedGrand51;
echo (array)$null_root === ["value" => 100] ? "NP100|" : "BAD|";
echo (array)$null_first === ["value" => null] ? "NFNULL|" : "BAD|";
echo (array)$null_second === ["value" => null] ? "NCNULL|" : "BAD|";
echo (array)$null_grand === ["value" => null] ? "NGNULL|" : "BAD|";
echo $null_first->value === false ? "NFALSE|" : "BAD|";
echo $null_second->value === 0 ? "NZERO|" : "BAD|";
echo $null_grand->parentRead() === 0 ? "HZERO|" : "BAD|";
$null_grand->value = 5;
echo (array)$null_grand === ["value" => 5] ? "N5|" : "BAD|";
echo $null_grand->value === 0 ? "NZERO|" : "BAD|";
