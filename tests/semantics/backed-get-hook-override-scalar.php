<?php
class HookOverrideParent36 {
    public int $value = 100 {
        get {
            echo "P:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->bias();
        }
    }
    private function bias() { return 1; }
    public function parentRead() { return $this->value; }
}
class HookOverrideChild36 extends HookOverrideParent36 {
    public int $value = 200 {
        get {
            echo "C:", __CLASS__, "/", static::class, "|";
            return $this->value + $this->bias();
        }
    }
    private function bias() { return 7; }
    public function childRead() { return $this->value; }
}
class HookOverrideGrand36 extends HookOverrideChild36 {
    private function bias() { return 99; }
}
$parent = new HookOverrideParent36;
echo "P", $parent->value, ":", ((array)$parent === ["value" => 100] ? "ONE" : "BAD"), "|";
$child = new HookOverrideChild36;
echo "C", $child->value, ":", ((array)$child === ["value" => 200] ? "ONE" : "BAD"), "|";
$grand = new HookOverrideGrand36;
echo "V", $grand->value, ":", ((array)$grand === ["value" => 200] ? "ONE" : "BAD"), "|";
echo "T", $grand->parentRead(), "|";
echo "U", $grand->childRead(), "|";
$grand->value = 300;
echo "W", $grand->value, ":", ((array)$grand === ["value" => 300] ? "ONE" : "BAD"), "|";
