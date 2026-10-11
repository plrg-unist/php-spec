<?php
class OrdinaryUnbackedLeaf50 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
function ordinaryUnbackedFresh50($tag) {
    global $weak_returned;
    echo "G", $tag, "|";
    $leaf = new OrdinaryUnbackedLeaf50;
    $leaf->tag = $tag;
    $weak_returned = WeakReference::create($leaf);
    return $leaf;
}
class OrdinaryUnbackedLifeParent50 {
    public mixed $value = null;
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        $leaf = $raw["value"];
        echo "B", $leaf->tag, "|";
    }
}
class OrdinaryUnbackedLifeBridge50 extends OrdinaryUnbackedLifeParent50 {}
class OrdinaryUnbackedLifeChild50 extends OrdinaryUnbackedLifeBridge50 {
    public mixed $value {
        get {
            echo "C|";
            return ordinaryUnbackedFresh50("R");
        }
    }
}
class OrdinaryUnbackedLifeGrand50 extends OrdinaryUnbackedLifeChild50 {}
$box = new OrdinaryUnbackedLifeGrand50;
$weak_box = WeakReference::create($box);
echo ((array)$box === [] ? "EMPTY_SLOT|" : "BAD|");
$stored = new OrdinaryUnbackedLeaf50;
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
