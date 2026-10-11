<?php
function hook_assign_tag33(mixed $value): string {
    return $value === null ? "N" : ($value === false ? "F" : (string) $value);
}
function hook_assign_fallback33(): int { echo "R|"; return 13; }
class HookAssignScalar33 {
    public int $mode = 0;
    public mixed $value = null {
        get {
            echo "G|";
            if ($this->mode === 0) { return false; }
            if ($this->mode === 1) { return 0; }
            return $this->value;
        }
    }
    public function inspect(): void {
        $kept = $this->value ??= hook_assign_fallback33();
        $snapshot = (array) $this;
        echo "T", hook_assign_tag33($kept), ":", hook_assign_tag33($snapshot["value"]), "|";
    }
}
$box = new HookAssignScalar33;
foreach ([0, 1, 2] as $mode) {
    $box->mode = $mode;
    $box->value = null;
    $kept = $box->value ??= hook_assign_fallback33();
    $snapshot = (array) $box;
    echo hook_assign_tag33($kept), ":", hook_assign_tag33($snapshot["value"]), "|";
    $box->mode = $mode;
    $box->value = null;
    $box->inspect();
}
