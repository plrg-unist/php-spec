<?php
function warn124($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class InitialParent124 {
    private int $ghost;
    public function readParent() {
        return $this->ghost; // READ124
    }
    public function __destruct() { echo 'D|'; }
}
class InitialChild124 extends InitialParent124 {
    private string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return '7'; }
}
set_error_handler('warn124');
$expectedLine = 6;
$child = new InitialChild124();
$result = 42;
echo 'I:';
try { $result = $child->readParent(); echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Typed property InitialParent124::$ghost must not be accessed before initialization' ? 'initial|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
