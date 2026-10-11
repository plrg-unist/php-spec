<?php
class InheritedStorageLeaf37 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
function inheritedStorageFresh37() {
    global $weak_returned;
    echo "G|";
    $leaf = new InheritedStorageLeaf37;
    $leaf->tag = "R";
    $weak_returned = WeakReference::create($leaf);
    return $leaf;
}
class InheritedStorageLifeParent37 {
    public mixed $value = 100 { get { return $this->value; } }
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        $leaf = $raw["value"];
        echo "B", $leaf->tag, "|";
    }
}
class InheritedStorageLifeChild37 extends InheritedStorageLifeParent37 {
    public mixed $value { get => inheritedStorageFresh37(); }
}
class InheritedStorageLifeGrand37 extends InheritedStorageLifeChild37 {}
$box = new InheritedStorageLifeGrand37;
$weak_box = WeakReference::create($box);
echo ((array)$box === [] ? "EMPTY|" : "BAD|");
$stored = new InheritedStorageLeaf37;
$stored->tag = "S";
$weak_stored = WeakReference::create($stored);
$box->value = $stored;
unset($stored);
echo "STORED|";
$kept = $box->parentRead();
echo "HELD|";
unset($box);
echo ($weak_box->get() === null ? "BN|" : "BL|");
echo ($weak_stored->get() === null ? "SN|" : "SL|");
echo ($weak_returned->get() === null ? "RN|" : "LIVE|");
unset($kept);
echo ($weak_returned->get() === null ? "RN|" : "LIVE|");
