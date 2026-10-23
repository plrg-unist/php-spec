<?php
function warn121($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class Probe121 {
    public function __destruct() {
        global $child, $expectedLine;
        echo 'V|';
        $receiver = $child;
        try { $value = $receiver->ghost; echo 'bad|'; } // READ121
        catch (Error $caught) {
            echo $caught->getMessage() === 'Typed property CleanupGet121::$ghost must not be accessed before initialization' ? 'typed|' : 'bad-message|';
            echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
            echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
        }
        unset($receiver);
        echo 'v|';
    }
}
class CleanupGet121 {
    public int $ghost = 0;
    public function __get($name) {
        global $make;
        echo 'G|';
        if ($make) { $make = false; $probe = new Probe121(); }
        echo 'g|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn121');
$expectedLine = 8;
$child = new CleanupGet121();
unset($child->ghost);
$make = true;
echo 'L:';
$result = $child->ghost;
echo 'A|', $result, '|';
$result = $child->ghost;
echo 'B|', $result, '|';
unset($child, $result);
restore_error_handler();
echo 'E|';
