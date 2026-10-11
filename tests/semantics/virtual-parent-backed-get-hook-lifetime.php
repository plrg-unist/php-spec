<?php
class VirtualBackedLeaf43 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
function virtualBackedFresh43($tag) {
    global $weak_returned;
    echo "G", $tag, "|";
    $leaf = new VirtualBackedLeaf43;
    $leaf->tag = $tag;
    $weak_returned = WeakReference::create($leaf);
    return $leaf;
}
class VirtualBackedLifeParent43 {
    public mixed $value { get => virtualBackedFresh43("P"); }
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        $leaf = $raw["value"];
        echo "B", $leaf->tag, "|";
    }
}
class VirtualBackedLifeBridge43 extends VirtualBackedLifeParent43 {}
class VirtualBackedLifeChild43 extends VirtualBackedLifeBridge43 {
    public mixed $value = null {
        get {
            $backing = $this->value;
            echo "C", $backing->tag, "|";
            return virtualBackedFresh43("R");
        }
    }
}
class VirtualBackedLifeGrand43 extends VirtualBackedLifeChild43 {}
$box = new VirtualBackedLifeGrand43;
$weak_box = WeakReference::create($box);
echo ((array)$box === ["value" => null] ? "NULL_SLOT|" : "BAD|");
$stored = new VirtualBackedLeaf43;
$stored->tag = "S";
$weak_stored = WeakReference::create($stored);
$box->value = $stored;
unset($stored);
echo "STORED|";
$kept = $box->parentRead();
echo "H", $kept->tag, "|";
echo ((array)$box === ["value" => $weak_stored->get()] ? "SLOT_S|" : "BAD|");
unset($box);
echo ($weak_box->get() === null ? "BN|" : "BL|");
echo ($weak_stored->get() === null ? "SN|" : "SL|");
echo ($weak_returned->get() === null ? "RN|" : "LIVE|");
unset($kept);
echo ($weak_returned->get() === null ? "RN|" : "LIVE|");
