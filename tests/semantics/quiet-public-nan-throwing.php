<?php
class QuietNanParent92 {
    public float $value = NAN;
    public function __destruct() { echo 'D|'; }
}
class QuietNanChild92 extends QuietNanParent92 {}
function warning92($no, $message, $file, $line) {
    global $child, $saved;
    echo 'H|';
    $saved->value = 0.0;
    $child = null;
    echo 'h|';
    throw new Exception('quiet-nan-stop');
}
$child = new QuietNanChild92();
$saved = $child;
set_error_handler('warning92');
echo 'X:', isset($child->value) ? 'I' : 'i', '|';
try { echo empty($child->value) ? 'T' : 'F', '|'; }
catch (Exception $caught) { echo 'C|'; }
restore_error_handler();
$saved = null;
echo 'E|';
