<?php
function hook_unset_virtual_read34(): int { echo "VG|"; return 9; }
class HookUnsetBacked34 {
    public int $value = 7 {
        get {
            echo "G|";
            try { unset($this->value); }
            catch (Error $e) { echo "A:", $e->getMessage(), ":", $e->getLine(), "|"; }
            return $this->value;
        }
    }
    public function inspect(): void {
        try { unset($this->value); }
        catch (Error $e) { echo "T:", $e->getMessage(), ":", $e->getLine(), "|"; }
        $snapshot = (array) $this;
        echo $snapshot["value"], "|";
    }

    public function __destruct() { echo "B|"; }
}
class HookUnsetVirtual34 {
    public int $value { get => hook_unset_virtual_read34(); }
    public function inspect(): void {
        try { unset($this->value); }
        catch (Error $e) { echo "VT:", $e->getMessage(), ":", $e->getLine(), "|"; }
        $snapshot = (array) $this;
        echo isset($snapshot["value"]) ? "SLOT|" : "EMPTY|";
    }

    public function __destruct() { echo "V|"; }
}
$box = new HookUnsetBacked34;
$weak = WeakReference::create($box);
try { unset($box->value); }
catch (Error $e) { echo "CV:", $e->getMessage(), ":", $e->getLine(), "|"; }
$snapshot = (array) $box;
echo $snapshot["value"], "|";
unset($snapshot, $e);
$box->inspect();
echo "READ:", $box->value, "|";
unset($box);
echo $weak->get() === null ? "N|" : "LIVE|";
$virtual = new HookUnsetVirtual34;
try { unset($virtual->value); }
catch (Error $e) { echo "VCV:", $e->getMessage(), ":", $e->getLine(), "|"; }
$snapshot = (array) $virtual;
echo isset($snapshot["value"]) ? "SLOT|" : "EMPTY|";
unset($snapshot, $e);
$virtual->inspect();
unset($virtual);
