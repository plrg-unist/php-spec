<?php
class VirtualBackedParent43 {
    public int $value {
        get {
            echo "P:", __CLASS__, "/", static::class, "|";
            return 7;
        }
    }
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class VirtualBackedBridge43 extends VirtualBackedParent43 {
    private function answer() { return 500; }
}
class VirtualBackedChild43 extends VirtualBackedBridge43 {
    public int $value = 200 {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->answer();
        }
    }
    private function answer() { return 13; }
}
class VirtualBackedGrand43 extends VirtualBackedChild43 {
    private function answer() { return 900; }
}
$parent = new VirtualBackedParent43;
$child = new VirtualBackedChild43;
$grand = new VirtualBackedGrand43;
echo (array)$parent === [] ? "EMPTY|" : "BAD|";
echo (array)$child === ["value" => 200] ? "C200|" : "BAD|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
echo $parent->value, "|";
echo $child->value, "|";
echo $grand->parentRead(), "|";
echo (array)$grand === ["value" => 200] ? "G200|" : "BAD|";
$grand->value = 300;
echo (array)$grand === ["value" => 300] ? "G300|" : "BAD|";
echo $grand->value, "|";
