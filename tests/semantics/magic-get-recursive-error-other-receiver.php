<?php
function warn121($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class OtherGet121 {
    public int $ghost = 0;
    public function __get($name) {
        global $first, $other;
        echo 'G|';
        if ($this === $first) { $receiver = $other; return $receiver->ghost; } // READ121
        return 9;
    }
}
set_error_handler('warn121');
$first = new OtherGet121();
$other = new OtherGet121();
unset($first->ghost, $other->ghost);
echo 'O:';
$result = $first->ghost;
echo 'A|', $result, '|';
unset($first, $other, $result);
restore_error_handler();
echo 'E|';
