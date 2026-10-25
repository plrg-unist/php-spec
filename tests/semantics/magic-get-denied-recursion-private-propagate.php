<?php
function warn122($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class PrivateParent122 {
    public function __get($name) {
        global $child;
        echo 'G|';
        $child = null;
        return $this->ghost; // READ122
    }
    public function __destruct() { echo 'D|'; }
}
class PrivateChild122 extends PrivateParent122 { private $ghost = 0; }
set_error_handler('warn122');
$expectedLine = 8;
$child = new PrivateChild122();
$result = 42;
echo 'P:';
try { $result = $child->ghost; echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Cannot access private property PrivateChild122::$ghost' ? 'private|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
