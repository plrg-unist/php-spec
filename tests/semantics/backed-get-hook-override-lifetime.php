<?php
class HookOverrideLeaf36 {
    public function __destruct() { echo "D|"; }
}
class HookOverrideLifeParent36 {
    public mixed $value = 100 {
        get { echo "P|"; return $this->value; }
    }
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        echo "B", $raw["value"], "|";
    }
}
class HookOverrideLifeChild36 extends HookOverrideLifeParent36 {
    public mixed $value = 200 {
        get {
            global $weak;
            $backing = $this->value;
            echo "C", $backing, "|";
            $leaf = new HookOverrideLeaf36;
            $weak = WeakReference::create($leaf);
            return $leaf;
        }
    }
}
class HookOverrideLifeGrand36 extends HookOverrideLifeChild36 {}
$box = new HookOverrideLifeGrand36;
$weak_box = WeakReference::create($box);
echo ((array)$box === ["value" => 200] ? "ONE|" : "BAD|");
$kept = $box->parentRead();
echo "HELD|";
unset($box);
echo ($weak_box->get() === null ? "BN|" : "BL|");
echo ($weak->get() === null ? "N|" : "LIVE|");
unset($kept);
echo ($weak->get() === null ? "N|" : "LIVE|");
