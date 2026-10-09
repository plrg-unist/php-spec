<?php
class VirtualLeaf30 {
    public function __destruct() { echo "D|"; }
}
function virtual_leaf30(): VirtualLeaf30 {
    echo "G|";
    return new VirtualLeaf30;
}
class VirtualHeap30 {
    public VirtualLeaf30 $value { get => virtual_leaf30(); }
    public function __destruct() { echo "B|"; }
}
$box = new VirtualHeap30;
$result = $box->value;
$weak = WeakReference::create($result);
echo $weak->get() === null ? "N|" : "L|";
unset($result);
echo $weak->get() === null ? "N|" : "L|";
$result = $box->value;
$weak2 = WeakReference::create($result);
unset($box);
echo $weak2->get() === null ? "N|" : "L|";
unset($result);
echo $weak2->get() === null ? "N|" : "L|";
