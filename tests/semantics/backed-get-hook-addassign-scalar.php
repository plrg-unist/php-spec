<?php
function hook_compound_right35(): int { echo "R|"; return 3; }
class HookCompoundScalar35 {
    public mixed $returned = null;
    public mixed $value = 100 {
        get { echo "G|"; $backing = $this->value; return $this->returned; }
    }
    public function probe(): void {
        $this->value = 100;
        $kept = ($this->value += hook_compound_right35());
        $snapshot = (array) $this;
        echo "T", $kept, ":", $snapshot["value"], "|";
    }
}
$box = new HookCompoundScalar35;
foreach ([null, false, 0, 7] as $returned) {
    $box->returned = $returned;
    $box->value = 100;
    $kept = ($box->value += hook_compound_right35());
    $snapshot = (array) $box;
    echo "C", $kept, ":", $snapshot["value"], "|";
    $box->probe();
}
