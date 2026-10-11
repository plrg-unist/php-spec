<?php
class RepeatedStorageRoot38 {
    public int $value = 100 {
        get {
            echo "P:", __CLASS__, "/", static::class, "|";
            return $this->value + 1;
        }
    }
    public function parentRead() { return $this->value; }
}
class RepeatedStorageFirst38 extends RepeatedStorageRoot38 {
    public int $value { get => $this->answer(); }
    private function answer() {
        echo "F:", __CLASS__, "/", static::class, "|";
        return 7;
    }
}
class RepeatedStorageBridge38 extends RepeatedStorageFirst38 {
    private function answer() { echo "BADBRIDGE|"; return 500; }
}
class RepeatedStorageSecond38 extends RepeatedStorageBridge38 {
    public int $value { get => $this->answer(); }
    private function answer() {
        echo "S:", __CLASS__, "/", static::class, "|";
        return 13;
    }
}
class RepeatedStorageGrand38 extends RepeatedStorageSecond38 {
    private function answer() { echo "BADGRAND|"; return 900; }
}
class RepeatedStorageUntypedRoot38 {
    public $value = "seed" { get { return $this->value; } }
}
class RepeatedStorageUntypedFirst38 extends RepeatedStorageUntypedRoot38 {
    public $value { get => false; }
}
class RepeatedStorageUntypedBridge38 extends RepeatedStorageUntypedFirst38 {}
class RepeatedStorageUntypedSecond38 extends RepeatedStorageUntypedBridge38 {
    public $value { get => 0; }
}
$parent = new RepeatedStorageRoot38;
$result = $parent->value;
echo "P", $result, ":", ((array)$parent === ["value" => 100] ? "ONE|" : "BAD|");
$first = new RepeatedStorageFirst38;
echo ((array)$first === [] ? "FE|" : "BAD|");
$result = $first->value;
echo "F", $result, "|";
$second = new RepeatedStorageSecond38;
echo ((array)$second === [] ? "SE|" : "BAD|");
$result = $second->value;
echo "S", $result, "|";
$grand = new RepeatedStorageGrand38;
echo ((array)$grand === [] ? "GE|" : "BAD|");
$result = $grand->parentRead();
echo "T", $result, "|";
$grand->value = 300;
echo ((array)$grand === ["value" => 300] ? "ONE300|" : "BAD|");
$result = $grand->value;
echo "W", $result, "|";
$untyped = new RepeatedStorageUntypedSecond38;
echo ((array)$untyped === ["value" => null] ? "NULLSLOT|" : "BAD|");
$result = $untyped->value;
echo ($result === 0 ? "ZERO|" : "BAD|");
$untyped->value = 5;
echo ((array)$untyped === ["value" => 5] ? "ONE5|" : "BAD|");
