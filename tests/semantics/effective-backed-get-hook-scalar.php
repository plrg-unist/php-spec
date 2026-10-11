<?php
class InheritedStorageParent37 {
    public int $value = 100 {
        get {
            echo "P:", __CLASS__, "/", static::class, "|";
            return $this->value + 1;
        }
    }
    public function parentRead() { return $this->value; }
}
class InheritedStorageChild37 extends InheritedStorageParent37 {
    public int $value { get => $this->answer(); }
    private function answer() {
        echo "C:", __CLASS__, "/", static::class, "|";
        return 7;
    }
}
class InheritedStorageGrand37 extends InheritedStorageChild37 {
    private function answer() { echo "BADGRAND|"; return 99; }
}
class InheritedStorageUntypedParent37 {
    public $value = "seed" { get { return $this->value; } }
}
class InheritedStorageUntypedChild37 extends InheritedStorageUntypedParent37 {
    public $value { get => false; }
}
$parent = new InheritedStorageParent37;
$result = $parent->value;
echo "P", $result, ":", ((array)$parent === ["value" => 100] ? "ONE|" : "BAD|");
$child = new InheritedStorageChild37;
echo ((array)$child === [] ? "CE|" : "BAD|");
$result = $child->value;
echo "C", $result, "|";
$grand = new InheritedStorageGrand37;
echo ((array)$grand === [] ? "GE|" : "BAD|");
$result = $grand->parentRead();
echo "T", $result, "|";
$grand->value = 300;
echo ((array)$grand === ["value" => 300] ? "ONE300|" : "BAD|");
$result = $grand->value;
echo "W", $result, "|";
$untyped = new InheritedStorageUntypedChild37;
echo ((array)$untyped === ["value" => null] ? "NULLSLOT|" : "BAD|");
$result = $untyped->value;
echo ($result === false ? "FALSE|" : "BAD|");
$untyped->value = 5;
echo ((array)$untyped === ["value" => 5] ? "ONE5|" : "BAD|");
