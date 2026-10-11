<?php
class OrdinaryBackedLeaf49 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
function ordinaryBackedFresh49($tag) {
    global $weak_returned;
    echo "G", $tag, "|";
    $leaf = new OrdinaryBackedLeaf49;
    $leaf->tag = $tag;
    $weak_returned = WeakReference::create($leaf);
    return $leaf;
}
class OrdinaryBackedLifeParent49 {
    public mixed $value = null;
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        $leaf = $raw["value"];
        echo "B", $leaf->tag, "|";
    }
}
class OrdinaryBackedLifeBridge49 extends OrdinaryBackedLifeParent49 {}
class OrdinaryBackedLifeChild49 extends OrdinaryBackedLifeBridge49 {
    public mixed $value = null {
        get {
            $backing = $this->value;
            echo "C", $backing->tag, "|";
            return ordinaryBackedFresh49("R");
        }
    }
}
class OrdinaryBackedLifeGrand49 extends OrdinaryBackedLifeChild49 {}
$box = new OrdinaryBackedLifeGrand49;
$weak_box = WeakReference::create($box);
echo ((array)$box === ["value" => null] ? "NULL_SLOT|" : "BAD|");
$stored = new OrdinaryBackedLeaf49;
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
