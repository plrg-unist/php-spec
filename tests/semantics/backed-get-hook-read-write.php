<?php
class HookBacked28 {
    public int $value = 7 {
        get {
            echo "G|";
            return $this->value + 1;
        }
    }
}
$box = new HookBacked28();
echo $box->value, "|";
echo $box->value, "|";
$box->value = 17;
echo $box->value, "|";
