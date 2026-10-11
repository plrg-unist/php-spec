<?php
function hook_coalesce_fallback32(): int { echo "R|"; return 13; }
class HookCoalesceScalar32 {
    public mixed $value = null {
        get { echo "G|"; return $this->value === false ? 7 : ($this->value === 7 ? false : $this->value); }
    }
    public function inspect(): void {
        $kept = $this->value ?? hook_coalesce_fallback32();
        echo $kept === false ? "TF|" : ($kept === 0 ? "T0|" : ($kept === 7 ? "T7|" : ($kept === 13 ? "T13|" : "TX|")));
    }
}
$box = new HookCoalesceScalar32;
foreach ([null, 0, false, 7] as $value) {
    $box->value = $value;
    $kept = $box->value ?? hook_coalesce_fallback32();
    echo $kept === false ? "F|" : ($kept === 0 ? "0|" : ($kept === 7 ? "7|" : ($kept === 13 ? "13|" : "X|")));
    $box->inspect();
}
