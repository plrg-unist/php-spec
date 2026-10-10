<?php
class HookQuietScalar31 {
    public mixed $value = null {
        get { echo "G|"; return $this->value === false ? 7 : $this->value; }
    }
    public function inspect(): void {
        echo isset($this->value) ? "TI|" : "TN|";
        echo empty($this->value) ? "TE|" : "TF|";
    }
}
$box = new HookQuietScalar31;
foreach ([null, 0, false, 7] as $value) {
    $box->value = $value;
    echo isset($box->value) ? "I|" : "N|";
    echo empty($box->value) ? "E|" : "F|";
    $box->inspect();
}
