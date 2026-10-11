<?php
class CovBackedAnimal44 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
class CovBackedDog44 extends CovBackedAnimal44 {}
function freshCovBacked44($tag) {
    global $weak_returned;
    echo "G", $tag, "|";
    $leaf = new CovBackedDog44;
    $leaf->tag = $tag;
    $weak_returned = WeakReference::create($leaf);
    return $leaf;
}
class CovBackedLifeParent44 {
    public CovBackedAnimal44|null $value { get => null; }
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        $leaf = $raw["value"];
        echo "B", $leaf->tag, "|";
    }
}
class CovBackedLifeBridge44 extends CovBackedLifeParent44 {}
class CovBackedLifeChild44 extends CovBackedLifeBridge44 {
    public CovBackedDog44|null $value = null {
        get {
            $backing = $this->value;
            echo "C", $backing->tag, "|";
            return freshCovBacked44("R");
        }
    }
}
class CovBackedLifeGrand44 extends CovBackedLifeChild44 {}
$box = new CovBackedLifeGrand44;
$weak_box = WeakReference::create($box);
echo (array)$box === ["value" => null] ? "NULL_SLOT|" : "BAD|";
$stored = new CovBackedDog44;
$stored->tag = "S";
$weak_stored = WeakReference::create($stored);
$box->value = $stored;
unset($stored);
echo "STORED|";
$kept = $box->parentRead();
echo "H", $kept->tag, "|";
echo ((array)$box)["value"] === $weak_stored->get() ? "SLOT_S|" : "BAD|";
unset($box);
echo $weak_box->get() === null ? "BN|" : "BAD|";
echo $weak_stored->get() === null ? "SN|" : "BAD|";
echo $weak_returned->get() !== null ? "LIVE|" : "BAD|";
unset($kept);
echo $weak_returned->get() === null ? "RN|" : "BAD|";
