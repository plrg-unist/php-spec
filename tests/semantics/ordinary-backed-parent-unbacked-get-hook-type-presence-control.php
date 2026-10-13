<?php
class OrdinaryPresenceRoot52 {
    public $value = 100;
    public function parentRead() { echo "H|"; return $this->value; }
}
class OrdinaryPresenceFirst52 extends OrdinaryPresenceRoot52 {
    public $value { get => $this->answer(); }
    private function answer() {
        echo "F:", self::class, "/", static::class, "|";
        return 7;
    }
}
class OrdinaryPresenceBridge52 extends OrdinaryPresenceFirst52 {
    private function answer() { return 500; }
}
class OrdinaryPresenceSecond52 extends OrdinaryPresenceBridge52 {
    public $value { get => $this->answer(); }
    private function answer() {
        echo "C:", self::class, "/", static::class, "|";
        return 13;
    }
}
class OrdinaryPresenceGrand52 extends OrdinaryPresenceSecond52 {
    private function answer() { return 900; }
}
$parent = new OrdinaryPresenceRoot52();
$first = new OrdinaryPresenceFirst52();
$child = new OrdinaryPresenceSecond52();
$grand = new OrdinaryPresenceGrand52();
$raw = (array) $parent;
echo $raw === ["value" => 100] ? "P100|" : "BAD|";
$raw = (array) $first;
echo $raw === ["value" => null] ? "FNULL|" : "BAD|";
$raw = (array) $child;
echo $raw === ["value" => null] ? "CNULL|" : "BAD|";
$raw = (array) $grand;
echo $raw === ["value" => null] ? "GNULL|" : "BAD|";
echo $first->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
$raw = (array) $grand;
echo $raw === ["value" => null] ? "GNULL|" : "BAD|";
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
