<?php
class BackedPresenceParent42 {
    public $value = 100 {
        get {
            echo "P:", __CLASS__, "/", static::class, "|";
            return $this->value;
        }
    }
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class BackedPresenceBridge42 extends BackedPresenceParent42 {
    private function answer() { return 500; }
}
class BackedPresenceChild42 extends BackedPresenceBridge42 {
    public $value = 200 {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
}
class BackedPresenceGrand42 extends BackedPresenceChild42 {
    private function answer() { return 900; }
}
$parent = new BackedPresenceParent42();
$child = new BackedPresenceChild42();
$grand = new BackedPresenceGrand42();
echo (array)$parent === ["value" => 100] ? "P100|" : "BAD|";
echo (array)$child === ["value" => 200] ? "C200|" : "BAD|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
