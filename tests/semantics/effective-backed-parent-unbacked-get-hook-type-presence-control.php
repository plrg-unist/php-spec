<?php
class EffectiveStorageRoot47 {
    public $value = 100 { get => $this->value; }
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class EffectiveStorageFirst47 extends EffectiveStorageRoot47 {
    public $value { get => 7; }
}
class EffectiveStorageBridge47 extends EffectiveStorageFirst47 { private function answer() { return 500; } }
class EffectiveStorageSecond47 extends EffectiveStorageBridge47 {
    public $value {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
}
class EffectiveStorageGrand47 extends EffectiveStorageSecond47 { private function answer() { return 900; } }
$root = new EffectiveStorageRoot47();
$first = new EffectiveStorageFirst47();
$second = new EffectiveStorageSecond47();
$grand = new EffectiveStorageGrand47();
$raw = (array)$root;
echo $raw === ["value" => 100] ? "R100|" : "BAD|";
$raw = (array)$first;
echo $raw === ["value" => null] ? "FNULL|" : "BAD|";
$raw = (array)$second;
echo $raw === ["value" => null] ? "SNULL|" : "BAD|";
$raw = (array)$grand;
echo $raw === ["value" => null] ? "GNULL|" : "BAD|";
echo $root->value, "|", $first->value, "|", $second->value, "|";
echo $grand->parentRead(), "|";
$raw = (array)$grand;
echo $raw === ["value" => null] ? "GNULL|" : "BAD|";
$grand->value = 300;
$raw = (array)$grand;
echo $raw === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
