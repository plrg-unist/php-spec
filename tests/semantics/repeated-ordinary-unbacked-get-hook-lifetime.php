<?php
class OrdinaryRepeatLeaf51 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
function ordinaryRepeatFresh51($tag) {
    global $weak_returned;
    echo "G", $tag, "|";
    $leaf = new OrdinaryRepeatLeaf51;
    $leaf->tag = $tag;
    $weak_returned = WeakReference::create($leaf);
    return $leaf;
}
class OrdinaryRepeatLifeRoot51 {
    public mixed $value = null;
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        $leaf = $raw["value"];
        echo "B", $leaf->tag, "|";
    }
}
class OrdinaryRepeatLifeFirst51 extends OrdinaryRepeatLifeRoot51 {
    public mixed $value {
        get {
            echo "F|";
            return ordinaryRepeatFresh51("F");
        }
    }
}
class OrdinaryRepeatLifeBridge51 extends OrdinaryRepeatLifeFirst51 {}
class OrdinaryRepeatLifeSecond51 extends OrdinaryRepeatLifeBridge51 {
    public mixed $value {
        get {
            echo "C|";
            return ordinaryRepeatFresh51("R");
        }
    }
}
class OrdinaryRepeatLifeGrand51 extends OrdinaryRepeatLifeSecond51 {}
$box = new OrdinaryRepeatLifeGrand51;
$weak_box = WeakReference::create($box);
echo ((array)$box === [] ? "EMPTY_SLOT|" : "BAD|");
$stored = new OrdinaryRepeatLeaf51;
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
