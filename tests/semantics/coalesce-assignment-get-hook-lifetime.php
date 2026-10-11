<?php
class HookAssignLeaf33 {
    public function __destruct() { echo "D|"; }
}
function hook_assign_leaf33(): object {
    global $weak;
    echo "G|";
    $leaf = new HookAssignLeaf33;
    $weak = WeakReference::create($leaf);
    return $leaf;
}
function hook_assign_fallback_leaf33(): object { echo "R|"; return new HookAssignLeaf33; }
class HookAssignVirtual33 {
    public object $value { get => hook_assign_leaf33(); }
    public function __destruct() { echo "B|"; }
}
$weak = null;
$box = new HookAssignVirtual33;
$kept = $box->value ??= hook_assign_fallback_leaf33();
echo $weak->get() === $kept ? "HELD|" : "X|";
unset($box);
echo $weak->get() === $kept ? "LIVE|" : "X|";
unset($kept);
echo $weak->get() === null ? "N|" : "X|";
