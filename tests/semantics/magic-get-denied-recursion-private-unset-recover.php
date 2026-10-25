<?php
function warn122($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class UnsetParent122 {
    public function __get($name) {
        global $expectedLine;
        echo 'G|';
        try { $value = $this->ghost; echo 'bad|'; } // READ122
        catch (Error $caught) {
            echo $caught->getMessage() === 'Cannot access private property UnsetChild122::$ghost' ? 'private|' : 'bad-message|';
            echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
            echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
        }
        echo 'g|';
        return 'ok';
    }
    public function __destruct() { echo 'D|'; }
}
class UnsetChild122 extends UnsetParent122 {
    private int $ghost = 0;
    public function clear() { unset($this->ghost); }
}
set_error_handler('warn122');
$expectedLine = 7;
$child = new UnsetChild122();
$child->clear();
echo 'U:';
$first = $child->ghost;
echo 'A|', $first, '|';
$second = $child->ghost;
echo 'B|', $second, '|';
unset($child, $first, $second);
restore_error_handler();
echo 'E|';
