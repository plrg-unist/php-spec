<?php
class VirtualOverrideLeaf39 {
    public $tag;
    public function __destruct() { echo "D", $this->tag, "|"; }
}
function virtualOverrideFresh39($tag) {
    global $weak_leaf;
    echo "G", $tag, "|";
    $leaf = new VirtualOverrideLeaf39;
    $leaf->tag = $tag;
    $weak_leaf = WeakReference::create($leaf);
    return $leaf;
}
class VirtualOverrideLifeParent39 {
    public mixed $value { get => virtualOverrideFresh39("P"); }
    public function parentRead() { return $this->value; }
    public function __destruct() { echo ((array)$this === [] ? "BEMPTY|" : "BAD|"); }
}
class VirtualOverrideLifeBridge39 extends VirtualOverrideLifeParent39 {}
class VirtualOverrideLifeChild39 extends VirtualOverrideLifeBridge39 {
    public mixed $value { get => virtualOverrideFresh39("C"); }
}
class VirtualOverrideLifeGrand39 extends VirtualOverrideLifeChild39 {}
$box = new VirtualOverrideLifeGrand39;
$weak_box = WeakReference::create($box);
echo ((array)$box === [] ? "EMPTY|" : "BAD|");
$kept = $box->parentRead();
echo "H", $kept->tag, "|";
echo ((array)$box === [] ? "READ_EMPTY|" : "BAD|");
try { $box->value = 7; }
catch (Error $error) { echo $error->getMessage(), ":", $error->getLine(), "|"; }
echo ((array)$box === [] ? "STILL_EMPTY|" : "BAD|");
echo ($weak_leaf->get() === null ? "N|" : "LIVE|");
unset($box);
echo ($weak_box->get() === null ? "BN|" : "BL|");
echo ($weak_leaf->get() === null ? "N|" : "LIVE|");
unset($kept);
echo ($weak_leaf->get() === null ? "N|" : "LIVE|");
