<?php
class HookCompoundReceiver35 {
    public int $label = 1;
    public bool $rebind = false;
    public mixed $returned = 7;
    public mixed $value = 100 {
        get {
            global $box, $weak;
            echo "G", $this->label, "|";
            $backing = $this->value;
            if ($this->rebind) {
                $box = new HookCompoundReceiver35;
                $box->label = 2;
                echo $weak->get() === $this ? "GL|" : "GN|";
            }
            return $this->returned;
        }
    }
    public function __destruct() {
        $snapshot = (array) $this;
        echo "D", $this->label, ":", $snapshot["value"], "|";
    }
}
function hook_compound_rebind_right35(): int {
    global $box, $weak;
    echo "R0|";
    $box = new HookCompoundReceiver35;
    $box->label = 2;
    echo $weak->get() === null ? "RN|" : "RL|";
    return 3;
}
function hook_compound_plain_right35(): int { echo "R|"; return 3; }
$box = new HookCompoundReceiver35;
$weak = WeakReference::create($box);
$kept = ($box->value += hook_compound_rebind_right35());
$snapshot = (array) $box;
echo $kept, ":", $snapshot["value"], "|";
unset($box);
$box = new HookCompoundReceiver35;
$box->rebind = true;
$weak = WeakReference::create($box);
$kept = ($box->value += hook_compound_plain_right35());
$snapshot = (array) $box;
echo $weak->get() === null ? "GN|" : "GL|";
echo $kept, ":", $snapshot["value"], "|";
unset($box);
