<?php
function virtual_write30(int $value): int { echo "R", $value, "|"; return $value; }
class VirtualGetter30 {
    public int $value {
        get { echo "G|"; return 7; }
    }
}
$box = new VirtualGetter30;
echo $box->value, "|", $box->value, "|";
try {
    echo "W|";
    $box->value = virtual_write30(23);
    echo "AFTER|";
} catch (Error $error) {
    echo $error->getMessage(), "|";
}
echo $box->value, "|";
