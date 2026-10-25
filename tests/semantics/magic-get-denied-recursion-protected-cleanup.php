<?php
function warn122($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class Probe122 {
    public function __destruct() {
        global $child, $expectedLine;
        echo 'V|';
        $receiver = $child;
        try { $value = $receiver->ghost; echo 'bad|'; } // READ122
        catch (Error $caught) {
            echo $caught->getMessage() === 'Cannot access protected property ProtectedChild122::$ghost' ? 'protected|' : 'bad-message|';
            echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
            echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
        }
        unset($receiver);
        echo 'v|';
    }
}
class ProtectedParent122 {
    protected int $ghost;
    public function __get($name) {
        global $make;
        echo 'G|';
        if ($make) { $make = false; $probe = new Probe122(); }
        echo 'g|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
class ProtectedChild122 extends ProtectedParent122 {}
set_error_handler('warn122');
$expectedLine = 8;
$child = new ProtectedChild122();
$make = true;
echo 'L:';
$result = $child->ghost;
echo 'A|', $result, '|';
$result = $child->ghost;
echo 'B|', $result, '|';
unset($child, $result);
restore_error_handler();
echo 'E|';
