<?php
class QuietRefNanParent93 {
    public float $value = NAN;
    public function __destruct() { echo 'D|'; }
}
class QuietRefNanChild93 extends QuietRefNanParent93 {}
function warning93($no, $message, $file, $line) {
    global $child, $saved, $old, $new;
    echo 'H|';
    $saved->value =& $new;
    $old = 0.0;
    $child = null;
    echo 'h|';
    return true;
}
$child = new QuietRefNanChild93();
$saved = $child;
$old =& $child->value;
$new = 1.0;
set_error_handler('warning93');
echo 'Z:', isset($child->value) ? 'I' : 'i', '|';
echo empty($child->value) ? 'T' : 'F', '|';
restore_error_handler();
$saved = null;
$old = null;
$new = null;
echo 'E|';
