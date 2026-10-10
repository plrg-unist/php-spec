<?php
class HookQuietLeaf31 {
    public function __destruct() { echo "D|"; }
}
function hook_quiet_leaf31(): object {
    global $weak;
    echo "G|";
    $leaf = new HookQuietLeaf31;
    $weak = WeakReference::create($leaf);
    return $leaf;
}
class HookQuietBox31 {
    public object $value { get => hook_quiet_leaf31(); }
    public function __destruct() { echo "B|"; }
}
$weak = null;
$box = new HookQuietBox31;
echo isset($box->value) ? "I|" : "N|";
echo $weak->get() === null ? "N|" : "L|";
echo empty($box->value) ? "E|" : "F|";
echo $weak->get() === null ? "N|" : "L|";
echo "LIVE|";
unset($box);
