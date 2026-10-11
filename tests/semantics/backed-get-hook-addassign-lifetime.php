<?php
class HookCompoundLeaf35 {
    public function __destruct() {
        global $weak_box;
        echo "D|", $weak_box->get() === null ? "BN|" : "BL|";
    }
}
class HookCompoundObject35 {
    public int $label = 1;
    public mixed $value = 100 {
        get {
            global $box, $weak_leaf;
            echo "G|";
            $backing = $this->value;
            $leaf = new HookCompoundLeaf35;
            $weak_leaf = WeakReference::create($leaf);
            $box = new HookCompoundObject35;
            $box->label = 2;
            return $leaf;
        }
    }
    public function __destruct() {
        $snapshot = (array) $this;
        echo "B", $this->label, ":", $snapshot["value"], "|";
    }
}
function hook_compound_error_right35(): int { echo "R|"; return 3; }
$weak_leaf = null;
$box = new HookCompoundObject35;
$weak_box = WeakReference::create($box);
try {
    $kept = ($box->value += hook_compound_error_right35());
} catch (TypeError $error) {
    echo "E:", $error->getMessage(), ":", $error->getLine(), "|";
}
echo $weak_leaf->get() === null ? "N|" : "LIVE|";
echo $weak_box->get() === null ? "BN|" : "BL|";
$snapshot = (array) $box;
echo $snapshot["value"], "|";
unset($box);
echo $weak_box->get() === null ? "BN|" : "BL|";
