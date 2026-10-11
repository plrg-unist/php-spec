<?php
class EffectiveBackedStorageRoot48 {
    public $value = 100 { get => $this->value; }
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class EffectiveBackedStorageFirst48 extends EffectiveBackedStorageRoot48 {
    public $value { get => 7; }
}
class EffectiveBackedStorageBridge48 extends EffectiveBackedStorageFirst48 { private function answer() { return 500; } }
class EffectiveBackedStorageSecond48 extends EffectiveBackedStorageBridge48 {
    public $value = 200 {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
}
class EffectiveBackedStorageGrand48 extends EffectiveBackedStorageSecond48 { private function answer() { return 900; } }
$root = new EffectiveBackedStorageRoot48();
$first = new EffectiveBackedStorageFirst48();
$second = new EffectiveBackedStorageSecond48();
$grand = new EffectiveBackedStorageGrand48();
$raw = (array)$root;
echo $raw === ["value" => 100] ? "R100|" : "BAD|";
$raw = (array)$first;
echo $raw === ["value" => null] ? "FNULL|" : "BAD|";
$raw = (array)$second;
echo $raw === ["value" => 200] ? "S200|" : "BAD|";
$raw = (array)$grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
echo $root->value, "|", $first->value, "|", $second->value, "|";
echo $grand->parentRead(), "|";
$raw = (array)$grand;
echo $raw === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
$raw = (array)$grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
