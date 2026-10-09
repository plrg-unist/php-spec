<?php
function hook_read28($box) { echo "H|"; return $box->value; }
class HookNested28 {
    public int $value = 7 {
        get {
            $before = $this->value;
            echo "G", $before, "|";
            $this->value = $before + 1;
            if ($before === 7) { return hook_read28($this); }
            return $this->value;
        }
    }
}
$box = new HookNested28();
echo $box->value, "|", $box->value, "|";
