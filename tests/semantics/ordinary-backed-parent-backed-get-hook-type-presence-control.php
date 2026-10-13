<?php
class OrdinaryBackedPresenceRoot53 {
    public $value = 100;
    public function parentRead() { echo "H|"; return $this->value; }
}
class OrdinaryBackedPresenceFirst53 extends OrdinaryBackedPresenceRoot53 {
    public $value { get => $this->answer(); }
    private function answer() {
        echo "F:", self::class, "/", static::class, "|";
        return 7;
    }
}
class OrdinaryBackedPresenceBridge53 extends OrdinaryBackedPresenceFirst53 {
    private function answer() { return 500; }
}
class OrdinaryBackedPresenceSecond53 extends OrdinaryBackedPresenceBridge53 {
    public $value = 200 { get => $this->value + $this->answer(); }
    private function answer() {
        echo "C:", self::class, "/", static::class, "|";
        return 13;
    }
}
class OrdinaryBackedPresenceGrand53 extends OrdinaryBackedPresenceSecond53 {
    private function answer() { return 900; }
}
$parent = new OrdinaryBackedPresenceRoot53();
$first = new OrdinaryBackedPresenceFirst53();
$child = new OrdinaryBackedPresenceSecond53();
$grand = new OrdinaryBackedPresenceGrand53();
$raw = (array) $parent;
echo $raw === ["value" => 100] ? "P100|" : "BAD|";
$raw = (array) $first;
echo $raw === ["value" => null] ? "FNULL|" : "BAD|";
$raw = (array) $child;
echo $raw === ["value" => 200] ? "C200|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
echo $first->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
$raw = (array) $grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
