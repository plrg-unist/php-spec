<?php
class MagicNanParent86 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        echo 'G|';
        return NAN;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicNanChild86 extends MagicNanParent86 {}
function rejectNan86($level, $message, $file, $line) {
    global $child;
    echo 'H:', $level, '/', $message, '/', $line, '|';
    $child = null;
    echo 'h|';
    throw new Exception('nan-stop');
}
set_error_handler('rejectNan86');
$child = new MagicNanChild86();
echo 'X:';
try { echo empty($child->value) ? 'T' : 'F', '|'; }
catch (Exception $caught) { echo 'C|'; }
restore_error_handler();
echo 'E|';
