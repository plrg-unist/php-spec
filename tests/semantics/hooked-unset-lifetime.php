<?php
function hook_unset_leaf_read34(mixed $value): mixed { echo "G|"; return $value; }
class HookUnsetLeaf34 { public function __destruct() { echo "D|"; } }
class HookUnsetBox34 {
    public mixed $value = null { get => hook_unset_leaf_read34($this->value); }
    public function inspect(): void {
        try { unset($this->value); }
        catch (Error $e) { echo "T:", $e->getMessage(), ":", $e->getLine(), "|"; }
    }

    public function __destruct() { echo "B|"; }
}
$box = new HookUnsetBox34;
$leaf = new HookUnsetLeaf34;
$weakLeaf = WeakReference::create($leaf);
$weakBox = WeakReference::create($box);
$box->value = $leaf;
unset($leaf);
try { unset($box->value); }
catch (Error $e) { echo "CV:", $e->getMessage(), ":", $e->getLine(), "|"; }
unset($e);
$box->inspect();
echo $weakLeaf->get() === null ? "DEAD|" : "LIVE|";
unset($box);
echo $weakLeaf->get() === null ? "LN|" : "LL|";
echo $weakBox->get() === null ? "BN|" : "BL|";
