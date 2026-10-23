<?php
function warn121($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class NullableGet121 {
    public ?int $ghost = null;
    public function __get($name) {
        global $expectedLine;
        echo 'G|';
        try { $value = $this->ghost; echo 'bad|'; } // READ121
        catch (Error $caught) {
            echo $caught->getMessage() === 'Typed property NullableGet121::$ghost must not be accessed before initialization' ? 'typed|' : 'bad-message|';
            echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
            echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
            $this->ghost = null;
        }
        echo $this->ghost === null ? 'n|' : 'bad|';
        echo 'g|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
set_error_handler('warn121');
$expectedLine = 8;
$child = new NullableGet121();
unset($child->ghost);
echo 'N:';
$first = $child->ghost;
echo 'A|', $first, '/', $child->ghost === null ? 'null|' : 'bad|';
unset($child->ghost);
$second = $child->ghost;
echo 'B|', $second, '/', $child->ghost === null ? 'null|' : 'bad|';
unset($child, $first, $second);
restore_error_handler();
echo 'E|';
