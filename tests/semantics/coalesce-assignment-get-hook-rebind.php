<?php
class HookAssignRebind33 {
    public mixed $value = null {
        get { echo "G|"; return $this->value; }
    }
    public function __destruct() { echo "H|"; }
}
function hook_assign_rebind33(): int {
    global $box, $weak;
    echo "R0|";
    $box = new HookAssignRebind33;
    echo $weak->get() === null ? "RN|" : "RL|";
    return 23;
}
$box = new HookAssignRebind33;
$weak = WeakReference::create($box);
$kept = $box->value ??= hook_assign_rebind33();
$snapshot = (array) $box;
echo $kept, ":", $snapshot["value"] === null ? "N" : $snapshot["value"], "|";
unset($box);
