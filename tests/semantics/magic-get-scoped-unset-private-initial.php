<?php
function warn123($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class InitialParent123 {
    private int $ghost;
    public function readParent() {
        $receiver = $this;
        return $receiver->ghost; // READ123
    }
    public function __destruct() { echo 'D|'; }
}
class InitialChild123 extends InitialParent123 {
    private string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return '7'; }
}
set_error_handler('warn123');
$expectedLine = 7;
$child = new InitialChild123();
$result = 42;
echo 'I:';
try { $result = $child->readParent(); echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Typed property InitialParent123::$ghost must not be accessed before initialization' ? 'initial|' : 'bad-message|';
    echo $caught->getLine() === $expectedLine ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($child, $caught);
restore_error_handler();
echo 'E|';
