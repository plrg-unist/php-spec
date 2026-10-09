<?php
class HookLeaf28 { public function __destruct() { echo "D|"; } }
class HookOwner28 {
    public HookLeaf28 $value {
        get {
            echo "G|";
            unset($GLOBALS['box']);
            return $this->value;
        }
    }
    public function __construct(HookLeaf28 $value) { $this->value = $value; }
    public function __destruct() { echo "B|"; }
}
$leaf = new HookLeaf28();
$weak = \WeakReference::create($leaf);
$box = new HookOwner28($leaf);
unset($leaf);
$copy = $box->value;
echo $weak->get() === null ? "N|" : "L|";
unset($copy);
echo $weak->get() === null ? "N|" : "L|";
