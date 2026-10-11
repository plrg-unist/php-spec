<?php
class PresenceParent41 {
    public $value {
        get {
            echo "P:", __CLASS__, "/", static::class, "|";
            return "root";
        }
    }
    public function parentRead() {
        echo "H|";
        return $this->value;
    }
}
class PresenceBridge41 extends PresenceParent41 {
    private function answer() { return 500; }
}
class PresenceChild41 extends PresenceBridge41 {
    public $value {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->answer();
        }
    }
    private function answer() { return 13; }
}
class PresenceGrand41 extends PresenceChild41 {
    private function answer() { return 900; }
}
$parent = new PresenceParent41;
$child = new PresenceChild41;
$grand = new PresenceGrand41;
echo (array) $parent === [] ? "PE|" : "PS|";
echo $parent->value, "|";
echo (array) $child === [] ? "CE|" : "CS|";
echo $child->value, "|";
echo (array) $grand === [] ? "GE|" : "GS|";
echo $grand->parentRead(), "|";
echo (array) $parent === [] && (array) $child === [] && (array) $grand === [] ? "EMPTY|" : "SLOTS|";
