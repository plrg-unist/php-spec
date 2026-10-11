<?php
class RepeatedStorageLeaf38 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
function repeatedStorageFresh38($tag) {
    global $weak_returned;
    echo "G", $tag, "|";
    $leaf = new RepeatedStorageLeaf38;
    $leaf->tag = $tag;
    $weak_returned = WeakReference::create($leaf);
    return $leaf;
}
class RepeatedStorageLifeRoot38 {
    public mixed $value = 100 { get { return $this->value; } }
    public function parentRead() { return $this->value; }
    public function __destruct() {
        $raw = (array)$this;
        $leaf = $raw["value"];
        echo "B", $leaf->tag, "|";
    }
}
class RepeatedStorageLifeFirst38 extends RepeatedStorageLifeRoot38 {
    public mixed $value { get => repeatedStorageFresh38("F"); }
}
class RepeatedStorageLifeBridge38 extends RepeatedStorageLifeFirst38 {}
class RepeatedStorageLifeSecond38 extends RepeatedStorageLifeBridge38 {
    public mixed $value { get => repeatedStorageFresh38("R"); }
}
class RepeatedStorageLifeGrand38 extends RepeatedStorageLifeSecond38 {}
$box = new RepeatedStorageLifeGrand38;
$weak_box = WeakReference::create($box);
echo ((array)$box === [] ? "EMPTY|" : "BAD|");
$stored = new RepeatedStorageLeaf38;
$stored->tag = "S";
$weak_stored = WeakReference::create($stored);
$box->value = $stored;
unset($stored);
echo "STORED|";
$kept = $box->parentRead();
echo "H", $kept->tag, "|";
unset($box);
echo ($weak_box->get() === null ? "BN|" : "BL|");
echo ($weak_stored->get() === null ? "SN|" : "SL|");
echo ($weak_returned->get() === null ? "RN|" : "LIVE|");
unset($kept);
echo ($weak_returned->get() === null ? "RN|" : "LIVE|");
