<?php
class QuietNanParent92 {
    public float $value = NAN;
    public function __destruct() { echo 'D|'; }
}
class QuietNanChild92 extends QuietNanParent92 {}
function warning92($no, $message, $file, $line) {
    global $child, $saved;
    echo 'H|';
    $child = null;
    echo 'h|';
    return true;
}
$child = new QuietNanChild92();
$saved = $child;
set_error_handler('warning92');
echo 'N:', isset($child->value) ? 'I' : 'i', '|';
echo empty($child->value) ? 'T' : 'F', '|';
restore_error_handler();
$saved = null;
echo 'E|';
