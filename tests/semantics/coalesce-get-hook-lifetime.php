<?php
class HookCoalesceLeaf32 {
    public function __destruct() { echo "D|"; }
}
function hook_coalesce_leaf32(): object {
    global $weak;
    echo "G|";
    $leaf = new HookCoalesceLeaf32;
    $weak = WeakReference::create($leaf);
    return $leaf;
}
function hook_coalesce_fallback_leaf32(): object { echo "R|"; return new HookCoalesceLeaf32; }
class HookCoalesceBox32 {
    public object $value { get => hook_coalesce_leaf32(); }
    public function __destruct() { echo "B|"; }
}
$weak = null;
$box = new HookCoalesceBox32;
$kept = $box->value ?? hook_coalesce_fallback_leaf32();
echo $weak->get() === $kept ? "HELD|" : "X|";
unset($box);
echo $weak->get() === $kept ? "LIVE|" : "X|";
unset($kept);
echo $weak->get() === null ? "N|" : "X|";
