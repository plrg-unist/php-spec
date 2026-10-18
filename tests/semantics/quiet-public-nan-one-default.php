<?php
class QuietNanParent92 {
    public float $value = NAN;
    public function __destruct() { echo 'D|'; }
}
class QuietNanChild92 extends QuietNanParent92 {}
function warning92($no, $message, $file, $line) {
    global $child, $saved;
    echo 'H|';
    $saved->value = 1.0;
    $child = null;
    echo 'h|';
    return false;
}
$child = new QuietNanChild92();
$saved = $child;
set_error_handler('warning92');
echo 'O:', isset($child->value) ? 'I' : 'i', '|';
echo empty($child->value) ? 'T' : 'F', '|';
restore_error_handler();
$saved = null;
echo 'E|';
